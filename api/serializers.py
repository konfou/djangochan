from rest_framework import serializers

from core.models import Board, Post


class BoardSerializer(serializers.ModelSerializer):
    last_post_timestamp = serializers.SerializerMethodField()
    last_thread_timestamp = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = [
            'ln', 'name', 'description',
            'last_post_timestamp', 'last_thread_timestamp',
        ]
        extra_kwargs = {
            'url': {'lookup_field': 'ln'}
        }

    def get_last_post_timestamp(self, obj):
        post_obj = obj.post_set.last()
        return post_obj.timestamp if post_obj is not None else ''

    def get_last_thread_timestamp(self, obj):
        post_obj = obj.post_set.filter(thread__isnull=True).last()
        return post_obj.timestamp if post_obj is not None else ''


class ThreadSerializer(serializers.ModelSerializer):
    replies_count = serializers.SerializerMethodField()
    last_reply_timestamp = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'pk', 'subject',
            'timestamp', 'author', 'tripcode', 'text',
            'image', 'filename',
            'closed', 'sticky',
            'replies_count', 'last_reply_timestamp',
        ]

    def get_replies_count(self, obj):
        return obj.post_set.count()

    def get_last_reply_timestamp(self, obj):
        post_obj = obj.post_set.last()
        return post_obj.timestamp if post_obj is not None else ''


class ReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = [
            'pk',  # 'thread', 'subject',
            'timestamp', 'author', 'tripcode', 'text',
            'image', 'filename',
        ]


class PostSerializer(serializers.ModelSerializer):
    # XXX: if done similar to forms by inheriting and excluding
    # following assertion error happens
    # > Cannot set both 'fields' and 'exclude' options on serializer <name>.
    # so it's kinda done the other way around
    class Meta:
        model = Post
        fields = ReplySerializer.Meta.fields + [
            'thread', 'subject',
        ]
