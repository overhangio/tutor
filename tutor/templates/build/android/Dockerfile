FROM ubuntu:18.04
MAINTAINER Régis Behmo <regis@behmo.com>

RUN apt update && \
  apt upgrade -y && \
  apt install -y wget unzip git openjdk-8-jre openjdk-8-jdk

RUN mkdir /openedx

# Install Android SDK
# Inspired from https://github.com/LiveXP/docker-android-sdk/blob/master/Dockerfile
ENV ANDROID_SDK_VERSION 4333796
ENV ANDROID_SDK_PATH /openedx/android-sdk
ENV ANDROID_HOME /openedx/android-sdk
RUN mkdir /openedx/android-sdk
WORKDIR /openedx/android-sdk
RUN wget https://dl.google.com/android/repository/sdk-tools-linux-${ANDROID_SDK_VERSION}.zip && \
    unzip sdk-tools-linux-${ANDROID_SDK_VERSION}.zip && \
    rm sdk-tools-linux-${ANDROID_SDK_VERSION}.zip

# Accept licenses
# https://developer.android.com/studio/command-line/sdkmanager
RUN yes | /openedx/android-sdk/tools/bin/sdkmanager "platforms;android-27" 1> /dev/null

# Install android app repo
RUN git clone https://github.com/edx/edx-app-android --branch master /openedx/edx-app-android
WORKDIR /openedx/edx-app-android

# Install gradle and all dependencies
RUN ./gradlew -v
RUN ./gradlew tasks

# User-customized config
COPY ./edx.properties ./OpenEdXMobile/edx.properties
RUN mkdir /openedx/config
RUN ln -s /openedx/config/gradle.properties ./OpenEdXMobile/gradle.properties

CMD ./gradlew assembleProdDebuggable && \
  cp OpenEdXMobile/build/outputs/apk/prod/debuggable/*.apk /openedx/data/
