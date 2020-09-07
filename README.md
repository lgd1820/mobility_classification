# mobility_classification


공공 데이터 포털에서 수집한 버스 궤적을 학습시켜 위드라이브 궤적에 대해 분류하여 버스 궤적을 검출해내는 것이 목표

데이터 보정
-----------
![image](https://user-images.githubusercontent.com/65576979/92385862-9f8fd200-f14d-11ea-8a78-79d7121287da.png)

위 데이터는 공공 데이터 포털에서 수집한 버스 궤적으로 위드라이브 궤적이 3초마다 저장되기 때문에 버스 궤적과 위드라이브 궤적의 간격의 갭이 큰 것을 볼 수 있다.

<pre><code>
</code></pre>
insert_missing_value.py
- 거리에 따른 결측치 값 추가 코드

impute_missing.py
- 결측치 값 보정 코드

missing_train.py
- 결측치 보정한 데이터 학습 코드

check_gps.py
- 학습된 모델을 통해 버스 궤적을 CSV로 만드는 
"# mobility_classification" 
