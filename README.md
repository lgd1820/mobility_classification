# mobility_classification


공공 데이터 포털에서 수집한 버스 궤적을 학습시켜 위드라이브 궤적에 대해 분류하여 버스 궤적을 검출해내는 것이 목표

데이터 보정
-----------
![image](https://user-images.githubusercontent.com/65576979/92385862-9f8fd200-f14d-11ea-8a78-79d7121287da.png)

위 데이터는 공공 데이터 포털에서 수집한 버스 궤적으로 위드라이브 궤적이 3초마다 저장되기 때문에 버스 궤적과 위드라이브 궤적의 간격의 갭이 큰 것을 볼 수 있다.
그렇기 때문에 버스 궤적 사이마다 결측치를 넣고 보정을 하여 간격의 갭을 매우게 된다.
<pre><code>
insert_missing_value.py
</code></pre>
위 코드는 거리에 따른 결측치 값을 추가하는 코드로 현재 100미터 간격으로 결측치를 추가한다.

<pre><code>
impute_missing.py
</code></pre>
위 코드는 결측치가 추가된 버스 궤적을 학습을 통해 결측치에 대한 값을 보정하여 궤적을 만든다.

결측치 보정을 통해 만들어진 궤적은 아래 사진과 같다.
빨간색의 궤적은 일반 버스 궤적이고 파란색 궤적은 보정된 버스 궤적이다.

![image](https://user-images.githubusercontent.com/65576979/92386395-af5be600-f14e-11ea-9b92-38daca2548f7.png)

데이터 전처리
------------
![image](https://user-images.githubusercontent.com/65576979/92451309-817eac00-f1f7-11ea-9f18-43921fba30d6.png)

우선 궤적을 이미지로 분류하여 학습을 하기위해 지도를 이미지형태의 데이터로 변환시킨다. 지도는 바둑판 모양의 CELL로 나눠지며, 각 CELL은 GPS의 구역을 담당하고 있고 궤적의 GPS는 CELL 구역에 맞는 번호로 바뀌어 저장이 된다. 즉, GPS 좌표가 입력 이미지의 pixel의 인덱스로 바뀌게 된다.
이미지 데이터 안에 들어가는 데이터는 위 그림에 나와있는 것 처럼 궤적이 다음 CELL 구역으로 넘어가기 전까지의 소요시간과 이동 방향(0~360도)이다.

missing_train.py
- 결측치 보정한 데이터 학습 코드

check_gps.py
- 학습된 모델을 통해 버스 궤적을 CSV로 만드는 
"# mobility_classification" 
