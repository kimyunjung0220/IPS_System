## 🎓 Welcome!

**이 프로젝트는 Linux 기반의 IPS(Intrusion Prevention System)를 제작하는 대학 프로젝트입니다.**  
**자세한 로드맵은 아래를 확인해 주시고, 업데이트 사항은 `Releases` 탭을 참고해주세요.**

---

## ✏️ 주요 기능

### 🚨 패킷 필터링

1. **Pyshark 기반 패킷 캡처**
   - Pyshark를 활용하여 패킷을 캡처한 후, 이를 웹 서버 및 탐지/차단 시스템으로 전달합니다.

2. **위협 탐지 및 차단**
   - 문자열 기반 탐지 및 차단 기능  
   - 공개된 악성 IP 기반 탐지 및 차단  
   - 사용자 정의 규칙에 따른 위협 탐지 및 차단

### 📈 모니터링 시스템

1. **데이터 시각화**
   - 웹 서버를 통해 패킷 및 트래픽 정보를 시각화하여 사용자에게 직관적인 데이터를 제공합니다.

2. **웹 기반 편의 기능**
   - 웹 UI를 통해 규칙 관리, 이벤트 로그, 계정 관리가 가능합니다.  
   - 시스템 내 모든 이벤트 및 로그를 확인할 수 있습니다.

---

##  🚩 개발 로드맵

> **개발 환경**: Ubuntu 22.04.05  
> **사용 언어**: Python  

✔️: 개발 완료  
✖️: 미완료 및 준비
🔶: 부분 완료  

### 🧱 패킷 관리
- ✔️ Pyshark 기반 패킷 캡처  
- ✖️ iptables를 이용한 패킷 차단  
- ✖️ 문자열 기반 위협 차단  

### 🖥️ 웹 페이지
- 🔶 로그인 및 회원 관리  
- ✖️ Admin 페이지  
- ✖️ 규칙 관리 기능  
- 🔶 패킷, 트래픽, 이벤트, 서버 사용량 시각화  
- ✖️ 로그 정보 확인  

### 📜 로그 시스템
- ✔️ 웹 페이지 접근 로그  
- ✖️ 계정 관리 로그  
- ✖️ 이벤트 관리 로그  
- 🔶 시스템 구동 로그  
- ✔️ 패킷 캡처 로그  

---

**마지막 수정일**: 2025-04-18

