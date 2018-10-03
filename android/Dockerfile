FROM ubuntu:16.04

RUN apt update && \
  apt upgrade -y && \
  apt install -y wget unzip git default-jre default-jdk

RUN mkdir /openedx

# Install Android SDK
# Inspired from https://github.com/LiveXP/docker-android-sdk/blob/master/Dockerfile
ENV ANDROID_SDK_VERSION 3859397
ENV ANDROID_SDK_PATH /openedx/android-sdk
ENV ANDROID_HOME /openedx/android-sdk
RUN mkdir /openedx/android-sdk
WORKDIR /openedx/android-sdk
RUN wget https://dl.google.com/android/repository/sdk-tools-linux-${ANDROID_SDK_VERSION}.zip && \
    unzip sdk-tools-linux-${ANDROID_SDK_VERSION}.zip && \
    rm sdk-tools-linux-${ANDROID_SDK_VERSION}.zip

# Install android app repo
RUN git clone https://github.com/edx/edx-app-android /openedx/edx-app-android
WORKDIR /openedx/edx-app-android

# User-customized config
COPY ./edx.properties ./OpenEdXMobile/edx.properties
RUN mkdir /openedx/config
RUN ln -s /openedx/config/gradle.properties ./OpenEdXMobile/gradle.properties

# Accept licenses
RUN yes | /openedx/android-sdk/tools/bin/sdkmanager --licenses

CMD ./gradlew assembleProdDebuggable && \
  cp OpenEdXMobile/build/outputs/apk/prod/debuggable/*.apk /openedx/data/
