/**
 * Created by littlepig on 2015/11/30.
 */
$(document).ready(function(){
	var code = getUrlParameter('code');
	$('#collapseOne').collapse('show');
	$('#collapseTwo').collapse('show');
	$('#collapseThree').collapse('hide');
	$('#collapseFour').collapse('hide');
	$.getJSON("data/getsportsdata?code="+code, function(data){
		openid = data.openid;
		renderByJson(data.data);
	});
	/*
	get_userinfo(function(data){
		openid = data.openid;
		nickname = data.nickname;
		headimgurl = data.headimgurl;
		headimgurl = data.headimgurl;
		$.getJSON("data/getsportsdata?openid="+openid, function(sportsData){
			renderByJson(sportsData);
		})
	});
	*/
})

function draw(){

	drawChart(getRandomArray(7), 7,"7-days-dis");
	drawChart(getRandomArray(7), 7, "7-days-steps");
	drawChart(getRandomArray(7), 7, "7-days-speed");
	drawChart(getRandomArray(7), 7, "7-days-calories");

	drawChart(getRandomArray(30), 30,"30-days-dis");
	drawChart(getRandomArray(30), 30, "30-days-steps");
	drawChart(getRandomArray(30), 30, "30-days-speed");
	drawChart(getRandomArray(30), 30, "30-days-calories");

	setDataText("7-days-dis-avg",  Math.floor(Math.random()*24)+1, "");
	setDataText("30-days-dis-avg",  Math.floor(Math.random()*24)+1, "");
	setDataText("7-days-steps-avg",  Math.floor(Math.random()*24)+1, "");
	setDataText("30-days-steps-avg",  Math.floor(Math.random()*24)+1, "");
	setDataText("7-days-calories-avg",  Math.floor(Math.random()*24)+1, "");
	setDataText("30-days-calories-avg",  Math.floor(Math.random()*24)+1, "");
	setExpertiseAdvise(Math.floor(Math.random()*3)+1,Math.floor(Math.random()*24)+1);
}

//draw the charts and change the data according to the json
function renderByJson(json){
	if (json.isnull == true) {
		draw();
		return 
	}
	drawChart(json["7-days-dis"], json["7-days-dis"].length,"7-days-dis");
	drawChart(json["7-days-steps"], json["7-days-steps"].length, "7-days-steps");
	drawChart(json["7-days-calories"], json["7-days-calories"].length, "7-days-calories");

	drawChart(json["30-days-dis"], 30,"30-days-dis");
	drawChart(json["30-days-steps"], 30, "30-days-steps");
	drawChart(json["30-days-calories"], 30, "30-days-calories");

	setDataText("7-days-dis-avg", json["7-days-dis-avg"], "");
	setDataText("30-days-dis-avg", json["30-days-dis-avg"], "");
	setDataText("7-days-steps-avg", json["7-days-steps-avg"], "");
	setDataText("30-days-steps-avg", json["30-days-steps-avg"], "");
	setDataText("7-days-calories-avg", json["7-days-calories-avg"], "");
	setDataText("30-days-calories-avg", json["30-days-calories-avg"], "");
	setExpertiseAdvise(json["yesterday-intensity"], json["7-days-intensity"]);
}

//draw a chart
function drawChart(data, dataLength, chartId){
	var dataPointArray = []
    for (var i = 0; i < dataLength; i += 1) {
        dataPointArray.push([i,data[i]]);
    }
	$.plot($("#" + chartId),
		[ { data: dataPointArray}], {
			series: {
				lines: { show: true },
				points: { show: true }
			},

			grid: { hoverable: true, clickable: true },
			xaxis: { min: 0, max: dataLength - 1 },
		});
}

//set the advise
function setExpertiseAdvise(yesterdayIntensity, sevenDayIntensity){
	var pattern = [];
	pattern[0] = [
		"如果你还没有运动的习惯，建议从小强度开始锻炼，最开始可以尝试坚持在操场每天走两圈，然后坚持5天左右再选择开始慢跑。",
		"建议可以慢慢增加锻炼时间，坚持按照轻微强度的练习再坚持5天左右。",
		"根据你的运动情况可以证明你的体力应该是比较好的，建议按照相同的训练强度和训练时间，一周之后看身体状况决定是否改变训练强度。",
		"建议你多关注自己身体的各方面情况，若有不适，请减小运动量。",
		"建议在运动前做好热身运动并准确衡量自己的身体状况，避免运动过量导致的受伤。",
	];
	pattern[1] = [
		"不要懒惰哦，继续坚持身体锻炼。建议此时更换自己喜欢的运动项目进行锻炼。",
		"建议根据自己的身体状况进行运动强度的增加，向中度强度的运动方向进行。",
		"运动状态十分良好，继续保持哦~",
		"运动强度的跨度略大，建议能多留意身体变化，若有不适，请立即减小运动量。",
		"建议在运动前做好热身运动并准确衡量自己的身体状况，避免运动过量导致的受伤。",
	];
	pattern[2] = [
		"不要懒惰哦，请继续坚持锻炼。",
		"虽然运动强度减小，但是能做到继续坚持运动，建议如果在自己运动范围内，仍然能继续加大运动强度至中度训练。",
		"身体锻炼情况十分好！请继续保持！",
		"身体锻炼情况很好，可以根据自己的身体状况适当增加难度。",
		"运动强度跨度还不算很大，但是还是建议能够在进行专业运动的时候，做足热身运动，避免拉伤等。",
	];
	pattern[3] = [
		"如果身体不适的话，可以适当休息，不过身体好了之后别忘了继续锻炼哦！",
		"建议在身体力所能及范围内加大运动强度。",
		"身体运动状态十分好，建议继续保持噢！",
		"身体运动状态很好，能与之前做到很好的保持，建议能够在运动时做好运动安全防护。",
		"运动强度能够慢慢上升，这一点已经做得很棒了，建议在专业运动时候做好准备活动以及运动过程中的安全防护。",
	];
	pattern[4] = [
		"如果身体不适的话，可以适当休息，不过身体好了之后别忘了继续锻炼哦！",
		"训练强度减小，建议适当提高训练强度，达到很好的锻炼效果。",
		"训练强度适中，建议继续保持，并按照自己对训练强度的标准，灵活做出相应调整。",
		"训练强度基本无变化，建议多留意身体状况，并按照自己的训练强度继续坚持。",
		"持续的专业训练，建议能够按照标准进行运动前的准备活动。并留意身体状况！",
	];
	$("#expertise-advise").text(pattern[sevenDayIntensity][yesterdayIntensity]);
}
//set data according to the data, "suffix" is the unit
function setDataText(idString, data, suffix){
	$("#" + idString).text(String(data) + suffix);
}
//test for random data
function getRandomArray(length){
	var data = [];
	for(var i = 0; i < length; i++){
		data.push(Math.floor(Math.random()*24)+1);
	}
	return data;
}