# BUS DATA

bus_correct_trajectory
---------------------
버스 보정 데이터가 저장된 폴더

bus_missing_trajectory
-----------------------
버스 좌표 사이에 결측치를 넣은 데이터가 저장된 폴더

bus_raw
-----------------------
공공데이터 포털에서 가져온 데이터의 원본
xml 형태

bus_station
-----------------------
버스 정거장의 좌표가 저장된 CSV파일 데이터

bus_trajectory
-----------------------
bus_raw의 데이터를 궤적별로(버스별로) 1차 전처리한 데이터가 저장된 폴더

버스 데이터 전처리
-----------------------

<pre><code>
bus_trajectory_grid.py
</code></pre>
버스 데이터를 100x100 형태의 npy 데이터로 바꾸는 코드

<pre><code>
insert_missing_value.py
</code></pre>
위 코드는 거리에 따른 결측치 값을 추가하는 코드로 현재 100미터 간격으로 결측치를 추가한다.

<pre><code>
impute_missing.py
</code></pre>
위 코드는 결측치가 추가된 버스 궤적을 학습을 통해 결측치에 대한 값을 보정하여 궤적을 만든다.

