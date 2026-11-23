---
slug: campusmate
title: 캠퍼스메이트
summary: 같은 대학교의 친구를 찾기 위한 어플. 틴더 + 에브리타임 느낌의 서비스
brief: Firestore 실시간 1:1, 그룹 채팅, 매칭, 커뮤니티, 푸시 알림 (Flutter)
period: 2024.03 – 2024.06
date: 2024-03-05
kind: hand
status: 개발 완료
tags: Flutter, Dart, Firebase
hue: 335
cover: assets/covers/campusmate.jpg
links: GitHub|https://github.com/Jokkilook/campusmate; YouTube|https://www.youtube.com/watch?v=pJp_Et6P1Sk
---
## 서비스 소개

같은 대학교의 친구를 찾기 위한 어플 (틴더 + 에브리타임 느낌의 서비스)

@video https://www.youtube.com/watch?v=pJp_Et6P1Sk

## 프로젝트 정보

- 팀 구성: 2인
- 개발 기간: 2024.03 ~ 2024.06
- 담당: 앱 기능 대부분 (채팅, 매칭, 프로필, 커뮤니티, 회원가입, 알림)
- 사용 기술: Flutter, Dart, Firebase (Auth, Firestore, Storage, Messaging)

## 역할

### 채팅 (1:1 / 그룹)

- Firestore 기반 실시간 채팅. 학교별로 데이터를 나눠 같은 학교 학생끼리만 채팅
- 1:1 채팅방 ID를 두 사용자 UID를 정렬해 만들어, 누가 먼저 시작해도 같은 방이 중복 생성되지 않게 처리
- 그룹 채팅: 인원 제한, 입장/퇴장 알림 메시지, 방장이 나가면 방 삭제
- 메시지 읽음 처리, 마지막 메시지 표시, 채팅방 검색
- 사진, 동영상 전송: 업로드 전 압축하고 동영상은 썸네일을 따로 만들어 저장

### 매칭 & 프로필

- 카드 형식 매칭 화면, 프로필 설정, 수정, 다른 사용자 프로필 보기
- 차단 사용자 관리

### 커뮤니티

- 게시글 작성, 수정, 댓글과 답글

### 회원가입 & 알림

- Firebase Authentication 회원가입, 선택한 학교의 이메일인지 확인하는 기능
- Firebase Messaging으로 특정 사용자에게 알림 발송

## 문제 해결

### 릴리즈 빌드에서만 화면이 회색으로 나오던 문제

- 원인: 위젯 배치(parentData) 오류가 디버그에서는 드러나지 않고 릴리즈 빌드에서 회색 화면으로 나타남
- 해결: 잘못 배치된 위젯 구조를 수정

### 배포용 APK에서 알림 아이콘이 깨지던 문제

- 해결: 배포 빌드용 알림 아이콘 설정을 수정
