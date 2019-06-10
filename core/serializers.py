#!/usr/bin/env python

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Python imports.
import logging
import datetime
import calendar

# Django imports.
from django.db import transaction
from django.http import Http404
# Rest Framework imports.
from rest_framework import serializers

# Third Party Library imports


# local imports.
from core.models import CustomUser, ExcersiceData, ExcersiceDataDificultyWise


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    def validate(self, data, *args, **kwargs):
        return super(UserCreateSerializer, self).validate(data, *args, **kwargs)

    @transaction.atomic()
    def create(self, validated_data):
        username = validated_data.get('username','')
        first_name = validated_data.get('first_name','')
        last_name = validated_data.get('last_name','')
        email = validated_data['email']
        user = CustomUser.objects.create(**validated_data)
        user.set_password(validated_data['password'])
        user.is_active = False
        user.save()
        return user

    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'id', 'password', 'first_name', 'last_name')


class UserListSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ('id', 'first_name', 'last_name', 'email', 'role', 'dificulty', 'is_email_verified')


class ExcersiceCreateSerializer(serializers.ModelSerializer):

    def validate(self, data, *args, **kwargs):
        return super(ExcersiceCreateSerializer, self).validate(data, *args, **kwargs)

    @transaction.atomic()
    def create(self, validated_data):
        user_id = validated_data.get('user_id','')
        reps = validated_data.get('reps','')
        steps = validated_data.get('steps','')
        excersice = ExcersiceData.objects.create(**validated_data)
        excersice.save()
        return excersice

    class Meta:
        model = ExcersiceData
        fields = ('user_id', 'reps', 'steps')


class ExcersiceListSerializer(serializers.ModelSerializer):

    class Meta:
        model = ExcersiceData
        fields = ('user_id', 'reps', 'steps')


class ExcersiceDifficulyCreateSerializer(serializers.ModelSerializer):

    def validate(self, data, *args, **kwargs):
        return super(ExcersiceDifficulyCreateSerializer, self).validate(data, *args, **kwargs)

    @transaction.atomic()
    def create(self, validated_data):
        difficulty = validated_data.get('difficulty','')
        excercise = validated_data.get('excercise','')
        reps = validated_data.get('reps','')
        steps = validated_data.get('steps','')
        excersice = ExcersiceData.objects.create(**validated_data)
        excersice.save()
        return excersice

    class Meta:
        model = ExcersiceDataDificultyWise
        fields = ('difficulty', 'excercise', 'reps', 'steps')


class ExcersiceDifficulyListSerializer(serializers.ModelSerializer):

    class Meta:
        model = ExcersiceDataDificultyWise
        fields = ('difficulty', 'excercise', 'reps', 'steps')

