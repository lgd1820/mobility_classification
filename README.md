# mobility_classification


공공 데이터 포털에서 수집한 버스 궤적을 학습시켜 위드라이브 궤적에 대해 분류하여 버스 궤적을 검출해내는 것이 목표

![bus_raw_data](./images/bus_raw_data.png)
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
