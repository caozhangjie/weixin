/**
 * Created by littlepig on 2015/11/29.
 */
$(document).ready(function(){

	$('#collapseOne').collapse('show');
	$('#collapseTwo').collapse('hide');
	$('#collapseThree').collapse('hide');
	var code = getUrlParameter('code');
	$.getJSON("data/getsleepdata?code="+code, function(data){
		openid = data.openid;
		renderByJson(data.data);
	});
	/*
	get_userinfo(function(data){
		openid = data.openid;
		nickname = data.nickname;
		headimgurl = data.headimgurl;
		headimgurl = data.headimgurl;
		$.getJSON("data/getsleepdata?openid="+openid, function(sleepData){
			
			renderByJson(sleepData);
		})
	});*/
});

//test drawing
function draw(){
	var weekChartId = "week_sleep_chart";
	var weekChartSleepTime = [6,7,5,7,6,7,6];
	var weekChartDeepSleepTime = [5,6,4,6,5,6,5];
	var monthChartId = "month_sleep_chart";
	var monthChartSleepTime = [6,7,5,7,6,7,6];
	var monthChartDeepSleepTime = [5,6,4,6,5,6,5];

	sleepChart(weekChartSleepTime, weekChartDeepSleepTime, 7, weekChartId);
	sleepChart(monthChartSleepTime, monthChartDeepSleepTime, 7, monthChartId);
	setDataText("7-days-avg", Math.floor(Math.random()*24)+1, "h");
	setDataText("30-days-avg", Math.floor(Math.random()*24)+1, "h");
	setDataText("7-days-deep-avg", Math.floor(Math.random()*24)+1, "h");
	setDataText("30-days-deep-avg", Math.floor(Math.random()*24)+1, "h");
	setSleepFluctuate("7-days-flac", 1);
	setSleepFluctuate("30-days-flac", 0);
	setSleepDeepRate("7-deep-avg", 1);
	setSleepDeepRate("30-deep-avg", 2);
}

//draw the charts and change the data according to the json
function renderByJson(json){
	//alert(JSON.stringify(json));
	if (json.isnull == true) {
		draw();
		return;
	}
	sleepChart(json["7-days-sleep"], json["7-days-deep-sleep"], json["7-days-sleep"].length, "week_sleep_chart");
	sleepChart(json["30-days-sleep"], json["30-days-deep-sleep"], json["30-days-deep-sleep"].length, "month_sleep_chart");
	setDataText("7-days-avg", json["7-days-avg"], "h");
	setDataText("30-days-avg",json["30-days-avg"], "h");
	setDataText("7-days-deep-avg", json["7-days-deep-avg"], "h");
	setDataText("30-days-deep-avg",json["30-days-deep-avg"], "h");
	setSleepFluctuate("7-days-flac", json["7-days-flac"]);
	setSleepFluctuate("30-days-flac", json["30-days-flac"]);
	setSleepDeepRate("7-deep-avg", json["7-days-avg"]);
	setSleepDeepRate("30-deep-avg", json["30-deep-avg"]);
	setExpertiseAdvise(json["stark-sleep"], json["avg-compare"], json["sleep-time-enough"], json["anxious"], json["regular"]);
}

//draw the sleep chart(including sleep time and deep sleep time)
function sleepChart(chartSleepTime,chartDeepSleepTime, days, chartId){

	var sleepTime = [], deepSleepTime = [];
    for (var i = 0; i < days; i += 1) {
        sleepTime.push([i,chartSleepTime[i]]);
        deepSleepTime.push([i, chartDeepSleepTime[i]]);
    }
	$.plot($("#" + chartId),
		[ { data: sleepTime, label: "sleep time"}, { data: deepSleepTime, label: "deep sleep time" } ], {
			series: {
				lines: { show: true },
				points: { show: true }
			},

			grid: { hoverable: true, clickable: true },
			xaxis: { min: 1, max: days },
			yaxis: { min: 1, max: 15 },
			colors: ["#F90", "#3C4049"]
		});
}

//set data according to the data, "suffix" is the unit
function setDataText(idString, data, suffix){
	$("#" + idString).text(String(data) + suffix);
}
//judge whether the fluctuation is normal
function setSleepFluctuate(idString, data){
	var result = "";
	if(data == 0){
		result = "Normal";
	}
	else{
		result = "Greatly";
	}
	$("#" + idString).text(result);
}
//judge whether the deep sleep rate is normal
function setSleepDeepRate(idString, data){
	var result = "";
	if(data == 0){
		result = "Low";
	}
	else{
		result = "Normal";
	}
	$("#" + idString).text(result);
}

//set the advise
function setExpertiseAdvise(stark_sleep, avg_compare, sleep_time, anxious, regular){
	if(sleep_time == 4){
		$("#expertise-advice").text("用户年龄太小，不适合佩戴手环！");
		return;
	}
	var sleep_time_string = [
		"",
		"您最近7天睡眠时间总体过多，",
		"您最近7天睡眠时间总体过少，",
		"您最近7天睡眠时间总体正常，"
	];
	var stark_sleep_string = [
		"每天睡眠时间刚好合适，",
		"其中一两天睡太久，",
		"其中一两天睡太少，",
	];
	if(avg_compare != 1 && avg_compare != 2){
		avg_compare = 3;
	}
	var avg_compare_string = [
		"",
		"和过去30天相比，您的睡眠时间明显变少，注意休息，",
		"和过去30天相比，您的睡眠时间明显增多，不可太懒哟，",
		"和过去30天相比，您的睡眠时间没有明显变化，",
	];
	if(anxious != 1 && anxious != 2){
		anxious = 0;
	}
	var anxious_string = [
		"",
		"最近7天您一直处于焦虑状态，建议您放松心情，不要给自己太大的压力，",
		"最近1个月您一直处于焦虑状态，建议您去学校的心理咨询中心释放一下情绪，",
	];
	if(regular != 0){
		regular = 1;
	}
	var regular_string = [
		"最近7天您睡眠不规律，请及时调整。养成良好的作息习惯，学习工作才会事半功倍",
		"最近7天您睡眠规律，请继续按时作息",
		
	];
	$("#expertise-advice").text(
		sleep_time_string[sleep_time] + 
		stark_sleep_string[stark_sleep] + 
		avg_compare_string[avg_compare] +
		anxious_string[anxious ] + 
		regular_string[regular] + '。'
		);
}