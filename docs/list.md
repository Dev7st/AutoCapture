✅ 반드시 필요:
1. 요구사항 명세서 (이미 완료)
2. rules.md

⚠️ 있으면 좋음:
3. 기술 설계서 (간략하게)
4. Task 분해 (TODO 리스트 수준)

❌ 없어도 됨:
- 상세한 클래스 다이어그램
- UML 다이어그램
- 과도하게 상세한 문서
```

### 💡 제 추천: **미니멀 버전**
```
1. 요구사항 명세서 ✅ (이미 있음)
2. rules.md ⭐⭐⭐⭐⭐ (필수)
3. 기술 설계서 (핵심만) ⭐⭐⭐
   - 아키텍처만
   - 주요 클래스만
   - 5~10페이지 정도
4. Task 체크리스트 ⭐⭐
   - 복잡한 WBS 말고
   - 간단한 TODO 리스트
```

**이유:**
- Claude Code는 rules.md를 **가장 중요하게** 참고
- 기술 설계서는 간단해도 개발 속도 향상
- Task는 너무 상세하면 유지보수 부담

---

## 2. Git 전략

### 🔀 Git Flow vs GitHub Flow vs 브랜치 없이

#### Option 1: Git Flow
```
main (배포용)
  ↓
develop (개발용)
  ↓
feature/얼굴감지
feature/GUI
feature/스케줄링
```

**장점**: 체계적, 롤백 쉬움  
**단점**: 혼자 쓰기엔 복잡, 오버엔지니어링

#### Option 2: GitHub Flow
```
main
  ↓
feature/얼굴감지
feature/GUI (완성되면 main에 merge)
```

**장점**: 간단, 빠름  
**단점**: 혼자면 큰 의미 없음

#### Option 3: Main 직접 커밋
```
main
 ↓ (직접 커밋)
```

**장점**: 가장 빠름, 간단  
**단점**: 실수하면 되돌리기 어려움

---

### 💡 제 추천: **Simple GitHub Flow (변형)**
```
main (항상 작동하는 버전)
  ↓
develop (개발 중)