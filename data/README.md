# bus_mode

insert_missing_value.py
- 거리에 따른 결측치 값 추가 코드

impute_missing.py
- 결측치 값 보정 코드

missing_train.py
- 결측치 보정한 데이터 학습 코드

check_gps.py
- 학습된 모델을 통해 버스 궤적을 CSV로 만드는 

<pre><code>
insert_missing_value.py
</code></pre>
위 코드는 거리에 따른 결측치 값을 추가하는 코드로 현재 100미터 간격으로 결측치를 추가한다.

<pre><code>
impute_missing.py
</code></pre>
위 코드는 결측치가 추가된 버스 궤적을 학습을 통해 결측치에 대한 값을 보정하여 궤적을 만든다.
