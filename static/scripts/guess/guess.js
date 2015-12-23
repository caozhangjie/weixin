$(document).ready(function(){
	var code = getUrlParameter('code');
		$.getJSON('data/getguesssubject?code='+code, function(data){
			openid = data.openid
			setsubjects(data.data);

			$('.set').click(function(){
				var subid = parseInt($(this).attr('id'));
				steps = $('#'+subid+'input').val();
				if (steps == 0) {
					alert("您还没有下注哦");
				} else {
					var choice;
					if ($('#'+subid+'A').attr('ifselect') == "true") {
						choice = "A";
					} else if ($('#'+subid+'B').attr('ifselect') == "true"){
						choice = "B";
					} else {
						alert("您还没有下注哦");
						return;
					}
					$.getJSON("data/saveuserbet?openid="+openid+"&choice="+choice+"&subid="+subid+"&steps="+steps, function(data){
						if (data.success == true){
							var new_steps = parseInt($('#'+subid+'steps'+choice).html())+parseInt(steps);
							$('#'+subid+'steps'+choice).html(new_steps.toString());
							alert("下注成功");
						} else {
							alert("下注失败,步数余额不足");
						}
					});
				}
			});

			$('.choice').click(function(){
				var subid = parseInt($(this).attr('id'));
				var self, other;
				if($(this).attr('ifselect') == 'false'){
					$(this).attr('ifselect', 'true');
					$(this).removeClass('btn-default').addClass('btn-info');
				}
				if (subid.toString()+'A'==$(this).attr('id')){
					self='A';
					other='B';
				} else {
					self='B';
					other='A';
				}
				if($('#'+subid+other).attr('ifselect') == 'true'){
					$('#'+subid+other).attr('ifselect', 'false');
					$('#'+subid+other).removeClass('btn-info').addClass('btn-default')
				}
			});
		});
});

function setsubjects(subjects){
	for (var i = subjects.length - 1; i >= 0; i--) {
		strHTML = '<div class="panel panel-primary" subid="'+subjects[i].id+
		'"><div class="panel-heading">'+subjects[i].content+
		'</div><div class="panel-body"><button type="button" class="btn btn-default choice" ifselect="false" id="'+subjects[i].id +
      'A">'+subjects[i].choiceA+'</button>当前投注总步数：<i id="'+subjects[i].id+'stepsA">'+subjects[i].stepsA+
      '</i><br><button type="button" class="btn btn-default choice" ifselect="false" id="'+subjects[i].id+'B">'+subjects[i].choiceB+
      '</button>当前投注总步数：<i id="'+subjects[i].id+'stepsB">'+subjects[i].stepsB+'</i><br>我的下注金额：<br><input class="form-control" id="'+subjects[i].id+
      'input" type="number"><button type="button" class="btn btn-danger set" id="'+subjects[i].id+
      'down">买定离手</button></div></div>';
		$('#panelgroup').append(strHTML);
	};
	if (subjects.length == 0) {
		$('body').html('<h>当前没有竞猜活动，稍后再来看看吧~</h>')
	}
}