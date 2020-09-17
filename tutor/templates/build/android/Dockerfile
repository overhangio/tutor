FROM docker.io/ubuntu:20.04
MAINTAINER Overhang.io <contact@overhang.io>

ENV DEBIAN_FRONTEND=noninteractive
RUN apt update && \
  apt upgrade -y && \
  apt install -y wget unzip git openjdk-8-jre openjdk-8-jdk

RUN mkdir /openedx

# Install Android SDK
# Inspired from https://github.com/LiveXP/docker-android-sdk/blob/master/Dockerfile
ENV ANDROID_SDK_VERSION 6200805
ENV ANDROID_SDK_PATH /openedx/android-sdk
ENV ANDROID_HOME /openedx/android-sdk
RUN mkdir ${ANDROID_HOME}
WORKDIR /openedx/android-sdk
RUN wget https://dl.google.com/android/repository/commandlinetools-linux-${ANDROID_SDK_VERSION}_latest.zip && \
    unzip commandlinetools-linux-${ANDROID_SDK_VERSION}_latest.zip && \
    rm commandlinetools-linux-${ANDROID_SDK_VERSION}_latest.zip

# Accept licenses
# https://developer.android.com/studio/command-line/sdkmanager
ARG ANDROID_API_LEVEL=28
RUN yes | /openedx/android-sdk/tools/bin/sdkmanager --sdk_root=${ANDROID_HOME} --install "platforms;android-$ANDROID_API_LEVEL" 1> /dev/null

# Install android app repo
ARG ANDROID_APP_REPOSITORY=https://github.com/edx/edx-app-android
ARG ANDROID_APP_VERSION=release/2.23.2
RUN git clone $ANDROID_APP_REPOSITORY --branch $ANDROID_APP_VERSION /openedx/edx-app-android
WORKDIR /openedx/edx-app-android

# Install gradle and all dependencies
RUN ./gradlew -v
RUN ./gradlew tasks

# User-customized config
COPY ./edx.properties ./OpenEdXMobile/edx.properties
RUN mkdir /openedx/config
RUN ln -s /openedx/config/gradle.properties ./OpenEdXMobile/gradle.properties
