# Django Rest
from rest_framework import serializers
from .models import Analytical, VideoAnalytical, StageAnalytical, StagePageAnalytical, PageSearchRecord


class StagePageModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = StagePageAnalytical
        fields = ('id', 'title')


class StagePageCompleteModelSerializer(serializers.ModelSerializer):
    stage = StagePageModelSerializer(many=False)

    class Meta:
        model = StagePageAnalytical
        fields = ('id', 'title', 'description', 'video', 'image', 'image_mobile', 'stage', 'nota', 'description_image')


class PageSearchRecordModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = PageSearchRecord
        fields = ('id', 'title', 'page', 'creator')


class StageModelSerializer(serializers.ModelSerializer):
    stage_page = StagePageModelSerializer(many=True, read_only=True)

    class Meta:
        model = StageAnalytical
        fields = ('id', 'title', 'stage_page')


class VideoModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = VideoAnalytical
        fields = ('id', 'title', 'duration', 'video', 'description', 'image')


class AnalyticalModelSerializer(serializers.ModelSerializer):
    analytical_video = VideoModelSerializer(many=True, read_only=True)
    analytical_stage = StageModelSerializer(many=True, read_only=True)

    class Meta:
        model = Analytical
        fields = ('id', 'description', 'manual', 'created', 'analytical_video', 'analytical_stage',)

