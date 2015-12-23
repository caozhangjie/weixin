$(document).ready(function(){
	get_userinfo(function(data){
		openid = data.openid;
		update_lives();
	});
});