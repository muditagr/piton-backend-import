# python imports

# Django imports
from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.http import HttpResponse, HttpResponseNotFound, Http404, HttpResponseRedirect
from django.core.mail import send_mail
from django.conf import settings

# Rest Framework imports
from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_jwt.serializers import JSONWebTokenSerializer
from rest_framework_jwt.views import JSONWebTokenAPIView

# local imports
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
# from .token import account_activation_token
from django.core.mail import send_mail

from core.models import User, ExcersiceData, ExcersiceDataDificultyWise
from core.serializers import (  UserCreateSerializer,
                                UserListSerializer,
                                ExcersiceCreateSerializer,
                                ExcersiceListSerializer,
                                ExcersiceDifficulyListSerializer,
                                ExcersiceDifficulyCreateSerializer
                            )
from core.utils import generate_jwt_token


class RegistrationAPIView(APIView):
    serializer_class = UserCreateSerializer
    permission_classes = (AllowAny,)
    authentication_classes = []

    __doc__ = "Registration API for user"

    def post(self, request, *args, **kwargs):

        try:
            user_serializer = UserCreateSerializer(data=request.data)
            if user_serializer.is_valid():
                user = user_serializer.save()
                data = generate_jwt_token(user, {})
                user_serializer = UserListSerializer(user)

                uid = urlsafe_base64_encode(force_bytes(user.pk)).decode()
                emailSubject = "Verification Email"
                emailLink = str(settings.BASEURL) + str("activation/?id=") + str(uid)
                emailBody = str('Click on the link for activation ') + str(emailLink)
                emailFrom = "no-reply@healthapi.com"
               
                from_email = settings.EMAIL_HOST_USER

                recipient_list = [request.data.get('email')]

                emailRes = send_mail(subject=emailSubject, message=emailBody, from_email=from_email,
                        recipient_list=recipient_list, fail_silently=False)
                        
                return Response({
                    'status': True,
                    #'token': data['token'],
                    #'data': user_serializer.data,
                    'message': 'Registered Successfully, Please verify your email to login'
                }, status=status.HTTP_200_OK)
            else:
                message = ''
                for error in user_serializer.errors.values():
                    message += " "
                    message += error[0]
                return Response({'status': False,
                                 'message': message},
                                status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'status': False,
                             'message': str(e)},
                            status=status.HTTP_400_BAD_REQUEST)


class LoginView(JSONWebTokenAPIView):
    serializer_class = JSONWebTokenSerializer

    __doc__ = "Log In API for user which returns token"

    @staticmethod
    def post(request):

        try:
            serializer = JSONWebTokenSerializer(data=request.data)
            if serializer.is_valid():
                serialized_data = serializer.validate(request.data)
                email = request.data.get('email')
                user = User.objects.get(email=email)
                user_serializer = UserListSerializer(user)
                if(user_serializer.data.get('is_email_verified') == True):
                    return Response({
                        'status': True,
                        'token': serialized_data['token'],
                        'data': user_serializer.data,
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({
                        'status': False,
                        'message': 'Your account is not activated yet, please check your email',
                    }, status=status.HTTP_200_OK)
            else:
                message = ''
                for error in serializer.errors.values():
                    message += " "
                    message += error[0]
                return Response({'status': False,
                                 'message': message},
                                status=status.HTTP_400_BAD_REQUEST)
        except (AttributeError, ObjectDoesNotExist):
            return Response({'status': False,
                             'message': "User does not exists"},
                            status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    @staticmethod
    def post(request):
        """
        Logout API for user
        """
        try:
            user = request.data.get('user', None)
            logout(request)
            return Response({'status': True,
                             'message': "logout successfully"},
                            status=status.HTTP_200_OK)
        except (AttributeError, ObjectDoesNotExist):
            return Response({'status': False},
                            status=status.HTTP_400_BAD_REQUEST)


class SettingAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request, *args, **kwargs):
        try:
            return Response({'status': True,
                             'message': "successfully Update"},
                            status=status.HTTP_200_OK)
        except (AttributeError, ObjectDoesNotExist):
            return Response({'status': False},
                            status=status.HTTP_400_BAD_REQUEST)


class doServerEmail(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        try:
            emailSubject = "Verification Email"
            emailBody = 'Click on the link for activation '
            
            from_email = settings.EMAIL_HOST_USER

            recipient_list = ['']

            emailRes = send_mail(subject=emailSubject, message=emailBody, from_email=from_email,
                recipient_list=recipient_list, fail_silently=False)
            return Response({'status': True,
                             'message': emailRes},
                            status=status.HTTP_200_OK)
        except (AttributeError, ObjectDoesNotExist):
            return Response({'status': False},
                            status=status.HTTP_400_BAD_REQUEST)


class UserAPIView(GenericAPIView):
    serializer_class = UserListSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        """
        List all the users.
        """
        try:
            users = User.objects.all()
            user_serializer = UserListSerializer(users, many=True)

            users = user_serializer.data
            return Response({'status': True,
                             'Response': users},
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'status': False, 'message': str(e)},
                            status=status.HTTP_400_BAD_REQUEST)


class EmailAPIView(APIView):

    __doc__ = "EmailAPIView API for user"

    def get(self, request, format=None):
        email = request.query_params.get('email')
        user = User.objects.filter(email=email)
        if user:
            return Response({'status': False,
                             'message': "Email Already Present"}, status=status.HTTP_200_OK)

        return Response({'status': True,
                         'message': ""}, status=status.HTTP_200_OK)


class ActivateApi(GenericAPIView):

    permission_classes = (AllowAny,)
    serializer_class = UserCreateSerializer
    __doc__ = "Activation API for user"
    def get(self, request):
        try:
            uid1 = request.query_params.get('id')
            uid = urlsafe_base64_decode(uid1).decode()
            user = User.objects.get(pk=uid)
            user.is_active = True
            user.is_email_verified = True
            user.save()
            return HttpResponse('Account is activated, please login into the app.')
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            return HttpResponse('Activation link is invalid!')

class ForgetAPIView(APIView):

    __doc__ = "ForgetAPIView API for user"

    def get(self, request, format=None):
        email = request.query_params.get('email')
        try:
            user = User.objects.get(email=email)
        except Exception as e:
            return Response({'status': False,
                             'message': "Email Not Present"}, status=status.HTTP_200_OK)

        subject = 'Thank you for registering to our site'
        message = render_to_string('registration/password_reset_email1.html', {
            'user': user,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activation_token.make_token(user),
        })
        from_email = settings.EMAIL_HOST_USER

        recipient_list = [user.email]

        send_mail(subject=subject, message=message, from_email=from_email,
                  recipient_list=recipient_list, fail_silently=False)

        return Response({'status': True,
                         'message': ""}, status=status.HTTP_200_OK)


class ForgetResetAPIView(APIView):

    __doc__ = "ForgetResetAPIView API for user"

    def post(self, request, format=None):

        code = request.data.get('code')
        password = request.data.get('password')

        try:

            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if user is not None and account_activation_token.check_token(user, token):

            return HttpResponseRedirect("http://18.223.218.199:3000")
        else:
            return HttpResponse('Activation link is invalid!')

        #     return Response({'status': False,
        #                      'message': "Email Already Present"}, status=status.HTTP_200_OK)

        # return Response({'status': True,
        #                  'message': ""}, status=status.HTTP_200_OK)


class ResendAPIView(APIView):

    __doc__ = "ResendAPIView API for user"

    def get(self, request, format=None):
        email = request.query_params.get('email')
        try:
            user = User.objects.get(email=email)
        except Exception as e:
            return Response({'status': False,
                             'message': "Email not Present"}, status=status.HTTP_200_OK)

        subject = "Thank you for registering to our site"
        message = render_to_string('send/index.html', {
            'user': user,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activation_token.make_token(user),
        })
        from_email = settings.EMAIL_HOST_USER

        recipient_list = [user.email]

        send_mail(subject=subject, message=message, from_email=from_email,
                  recipient_list=recipient_list, fail_silently=False)

        return Response({'status': True,
                         'message': ""}, status=status.HTTP_200_OK)


class UpdateDificultyView(APIView):
    serializer_class = UserListSerializer
    permission_classes = (IsAuthenticated,)

    def put(self, request, *args, **kwargs):
        try:
            dificulty = request.data.get('dificulty')
            serializer = self.serializer_class(request.user)
            serializer = UserListSerializer(
                request.user, data=request.data,  partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'status': True,
                              'dificulty': serializer.data,
                             'message': "successfully Update"},
                            status=status.HTTP_200_OK)
        except (AttributeError, ObjectDoesNotExist):
            return Response({'status': False},
                            status=status.HTTP_400_BAD_REQUEST)


class ExcersiceListView(APIView):
    serializer_class = UserListSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        try:
            serializer = self.serializer_class(request.user)
            user_id = serializer.data.get('id')
            gyms = ExcersiceData.objects.filter(user_id=user_id)
            gym_serializer = ExcersiceListSerializer(gyms, many=True)
            gyms = gym_serializer.data
            return Response({'status': True,
                              'data': gyms
                            },status=status.HTTP_200_OK)
        except (AttributeError, ObjectDoesNotExist):
            return Response({'status': False},
                            status=status.HTTP_400_BAD_REQUEST)

class ExcersiceCreateView(APIView):
    serializer_class = UserListSerializer
    permission_classes = (IsAuthenticated,)
    def post(self, request, *args, **kwargs):
        try:
            reps = request.data.get('reps')
            steps = request.data.get('steps')
            serializer = self.serializer_class(request.user)
            user_id = serializer.data.get('id')

            gym = {
                'user_id': user_id,
                'reps': reps,
                'steps': steps
            }

            gym_serializer = ExcersiceCreateSerializer(data=gym)
            if gym_serializer.is_valid():
                gym_data = gym_serializer.save()
                gym_serializer = ExcersiceListSerializer(gym_data)
                return Response({
                    'status': True,
                    'data': gym_serializer.data,
                }, status=status.HTTP_200_OK)
            else:
                message = ''
                for error in gym_serializer.errors.values():
                    message += " "
                    message += error[0]
                return Response({'status': False,
                                 'message': message},
                                status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'status': False,
                             'message': str(e)},
                            status=status.HTTP_400_BAD_REQUEST)


class ExcersiceDifficultListView(APIView):
    permission_classes = (AllowAny,)
    def get(self, request, format=None):
        try:
            gyms = ExcersiceDataDificultyWise.objects.all()
            gym_serializer = ExcersiceDifficulyListSerializer(gyms, many=True)
            gyms = gym_serializer.data
            return Response({'status': True,
                              'data': gyms
                            },status=status.HTTP_200_OK)
        except (AttributeError, ObjectDoesNotExist):
            return Response({'status': False},
                            status=status.HTTP_400_BAD_REQUEST)


class ExcersiceDifficultCreateView(APIView):
    permission_classes = (AllowAny,)
    def post(self, request, *args, **kwargs):
        try:
            reps = request.data.get('reps')
            steps = request.data.get('sets')
            excercise = request.data.get('excercise')
            difficulty = request.data.get('difficulty')
            
            difexc = {
                'difficulty': difficulty,
                'excercise': excercise,
                'reps': reps,
                'steps': steps
            }

            excdif_serializer = ExcersiceDifficulyCreateSerializer(data=difexc)
            if excdif_serializer.is_valid():
                excdif_data = excdif_serializer.save()
                excdif_serializer = ExcersiceDifficulyListSerializer(excdif_data)
                return Response({
                    'status': True,
                    'data': excdif_serializer.data,
                }, status=status.HTTP_200_OK)
            else:
                message = ''
                for error in gym_serializer.errors.values():
                    message += " "
                    message += error[0]
                return Response({'status': False,
                                 'saf': message},
                                status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'status': False,
                             'sadf': str(e)},
                            status=status.HTTP_400_BAD_REQUEST)