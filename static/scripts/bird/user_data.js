$(document).ready(function(){
	get_userinfo(function(data){
		openid = data.openid;
		nickname = data.nickname;
		headimgurl = data.headimgurl;
		update_lives();
	});
});