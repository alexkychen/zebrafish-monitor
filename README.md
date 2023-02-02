# Zebrafish Activity Monitor System
The system utilizes infrared (IR) sensors to measure the activity of zebrafish. It is designed to collect data on the movement and behavior of the fish in real-time, and use this information to provide insights into the health and well-being of the fish. The IR sensors are used to detect the movement of fish, which can be used as a proxy for activity levels. The system also uses machine learning algorithms or statistical models to process the data and generate predictions about future activity levels. The goal of the project is to provide a simple and reliable way to monitor zebrafish activity and to help researchers and facility managers understand and manage the health of the fish in their care.

## Activity levels were quantified by counting the number of IR beam breaks.
![activity_measured_by_IR](pic/activity_measured_by_IR.jpg)
This is achieved by using a pair of IR emitter and receiver, with the emitter emitting a beam of infrared light and the receiver detecting the beam when it is interrupted by a fish passing between them. The system counts the number of times the IR beam is broken, which is used as a proxy for the level of fish activity in the area being monitored. The more IR beam breaks that are detected, the higher the level of fish activity. By quantifying the activity levels of fish in this way, the system provides a reliable and non-invasive way to gather data on the movement and behavior of the fish. In practice, there are four sets of IR emitters and receivers around a rearing container and the beam break counts of four sensors represent the overall activity level of all fish in the container.

## Example of activity data
![example_data](pic/example_data.png)
The above plot shows the mean number of IR beam breaks at a 15-minutes frequency over a period of 6 days, which is used to indicate the activity levels of zebrafish. The data displayed in the plot exhibit a clear day-night cycle pattern, with the number of beam breaks fluctuating over time. The highest activity levels are shown as spikes in the data and occur during feeding time, suggesting that the fish are more active when they are being fed. The day-night cycle pattern can be explained by the natural behavior of the fish, which are more active during the day and rest at night (gray area). The plot provides a visual representation of the activity levels of the fish over time, which can be used to gain insights into their behavior and health.

### Interactive data viewer

## Exploratory data analysis

### Activity data decomposition (additive ETS decomposition)
![](pic/ETS_decomposition.png)

### Data stationarity

### ACF and PACF
![](pic/ACF_PACF.png)

## Predict future activity
