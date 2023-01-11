from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.response import Response

from core.models import Board, Post
from .serializers import BoardSerializer, ThreadSerializer, ReplySerializer


class BoardViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    lookup_field = 'ln'


class ThreadViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Post.objects.all()
    serializer_class = ThreadSerializer

    def list(self, request, board_ln=None):
        queryset = Post.objects.filter(
            board__ln=board_ln, thread__isnull=True).order_by('-bump')
        serializer = ThreadSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, board_ln=None, pk=None):
        queryset = Post.objects.filter(thread=pk).order_by('timestamp')
        serializer = ReplySerializer(queryset, many=True)
        return Response(serializer.data)
