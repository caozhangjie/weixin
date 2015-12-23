var STEP_METER = 0.6;
var update_dis = function () {
	$('#goal_dis').val(Math.floor((Number($('#goal_step').val()) * STEP_METER).toString()));
};
var update_step = function () {
	$('#goal_step').val(Math.floor((Number($('#goal_dis').val()) / STEP_METER).toString()));
};
function set_userinfo(){
	var danger = false;
	var age = $('#age').val();
	var height = $('#height').val();
	var weight = $('#weight').val();
	if (!(/(^[1-9]\d*$)/.test(age))){
		alert('请确认年龄(岁)为一正整数');
		danger = true;
	}
	if (!(/(^[1-9]\d*$)/.test(weight))){
		alert('请确认体重(kg)为一正整数');
		danger = true;
	}
	if (!(/(^[1-9]\d*$)/.test(height))){
		alert('请确认身高(cm)为一正整数');
		danger = true;
	}
	if(danger){
		$('#registe').attr({'class': 'btn btn-danger'});
		danger = false;
		return;
	}
	else{
		$('#registe').attr({'class': 'btn btn-success'});
	}
	$.post("data/register",{
		sex:$('#sex').val(),
		age:age,
		height:height,
		weight:weight,
		goal_step:$('#goal_step').val(),
		openid:openid
	}, showinfo);
}
$(document).ready(function(){
	$('#goal_step').on('input', update_dis);
	$('#goal_dis').on('input', update_step);
	get_userinfo(function(data){
		openid = data.openid;
		nickname = data.nickname;
		headimgurl = data.headimgurl;
		$.getJSON("data/ifregistered/"+openid, function(data){
			if (data.ifregistered == true) {
				$('#sex').val(data.sex);
				$('#age').val(data.age);
				$('#height').val(data.height);
				$('#weight').val(data.weight);
				$('#goal_step').val(data.goal_step);
				$('#goal_dis').val(Math.floor((data.goal_step * STEP_METER).toString()));
				$('#registe').attr({'value': 'MODIFY'});
			}else{
				$('#registe').attr({'value': 'REGISTE'});
			}
		});
	});
});
function showinfo() {
	alert("success!");
}