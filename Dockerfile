# Docker 설정 파일: 컨테이너 이미지를 만들기 위한 내용

# pull official base image
FROM python:3.10-alpine

# set work directory
WORKDIR /usr/src/app

# set environment variables
#   Docker 에서는 필요 없으므로 .pyc 파일 생성하지 않도록 함
ENV PYTHONDONTWRITEBYTECODE 1
#   Python log 를 버퍼링 없이 출력
ENV PYTHONUNBUFFERED 1

RUN apk update
RUN apk add postgresql-dev gcc python3-dev musl-dev zlib-dev jpeg-dev

# 현재 디렉토리의 파일을 모두 작업 폴더로 복사
COPY . /usr/src/app/

# install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt