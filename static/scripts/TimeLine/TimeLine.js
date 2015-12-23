/**
 * Created by littlepig on 2015/12/20.
 */
$(document).ready(function(){
    get_userinfo(function(data){
		openid = data.openid;
		nickname = data.nickname;
		headimgurl = data.headimgurl;
		headimgurl = data.headimgurl;
		$.getJSON("data/getTimeLineData?openid="+openid, function(data){
			renderByJson(data);
		})
	});
});

function renderByJson(json){
    var data;
    if (json.isnull == true) {
		data = [];
	}else{
        data = json.data;
    }
    addDays(data.length);
    for(var j = 0; j < data.length; j++){
        addItem(data[j][0]["startTime"].split(" ")[0], j);
        var i = 0;
        for(; i < data[j].length; i++){
            addOneElement(getHTMLDict(data[j][i]), j);
            if(("none" in data[j][i])  || !("type" in data[j][i])){
                i = data[j].length;
            }
        }
    }
}

function addDays(days){
    if(days > 1){
       
        for(var i = 1; i < days; i++){
             var newCarousel = $("<li data-target=\"#myCarousel\" data-slide-to=\" " + i +" \"></li>");
            var newItem = $(
                " <div id=\"item" + i + "\" class=\"item\"> " +
                    "<section id=\"cd-timeline" + i +"\" class=\"cd-container\">" +

                    "</section>"+
                " </div> "
            );
            $("#carousel").append(newCarousel);
            $("#carousel-inner").append(newItem);
        }
    }
    else if(days == 0){
        data = {};
        data["imgString"] = "";
        data["dataString"] = "There's no data in our database.";
        addOneElement(data, 0);
    }
}

function addItem(date, j){
    $("#item"+j).append("<div class=\"carousel-caption\"><font style=\"color:black\">"+ date + "</font></div>");
    $("#item"+j).append("<div style=\"height:20px;\"></div>");
}

function addOneElement(data, num){
    var newElement =  $("<div class=\"cd-timeline-block\">" +
            "<div class=\"cd-timeline-img cd-picture\"> " +
                data["imgString"] +
            "</div>" +
            "<div class=\"cd-timeline-content\">" +
                data["dataString"] +
            "</div>" +
            "</div>");
    $("#cd-timeline" + num).append(newElement);
}

function getHTMLDict(data){
    if("none" in data){
        return {
            imgString:getImgString(""),
            dataString:getH2Element("Don't forget uploading data~")
        }
    }
    else if(!("type" in data)){
        return {
            imgString:getImgString(""),
            dataString:getH2Element("Don't forget uploading data!~")
        }
    }
    else if(data["type"] == 1){
        return {
            imgString:getImgString("sleep.png"),
            dataString:getH2Element("Sleep") +
                getTime(data["startTime"])
        }
    }
    else if(data["type"] == 2){
        if(data["subType"] == 1){
            return {
                imgString:getImgString("warm_up.png"),
                dataString:getH2Element("Warm Up") +
                    getTime(data["startTime"])
            }
        }
        else if(data["subType"] == 2){
            return {
                imgString:getImgString("sport_walk.png"),
                dataString:getH2Element("Sport Walk") +
                    getTime(data["startTime"])
            }
        }
        else if(data["subType"] == 3){
            return {
                imgString:getImgString("ball.png"),
                dataString:getH2Element("Ball") +
                    getTime(data["startTime"])
            }
        }
        else if(data["subType"] == 4){
            return {
                imgString:getImgString("run.png"),
                dataString:getH2Element("Run") +
                    getTime(data["startTime"])
            }
        }
        else if(data["subType"] == 5){
            return {
                imgString:getImgString("swim.png"),
                dataString:getH2Element("Swim") +
                    getTime(data["startTime"])
            }
        }
    }
    else{
        if(data["subType"] == 1){
           return {
                imgString:getImgString("coffee.png"),
                dataString:getH2Element("Office") +
                    getTime(data["startTime"])
           }
        }
        else if(data["subType"] == 2){
            return {
                imgString:getImgString("walk.png"),
                dataString:getH2Element("Walk") +
                    getTime(data["startTime"])
            }
        }
        else if(data["subType"] == 3){
            return {
                imgString:getImgString("car.png"),
                dataString:getH2Element("Car") +
                    getTime(data["startTime"])
            }
        }
    }
}

function getImgString(data){
    return "<img src=\"/TimeLine/" + data  + "\"alt=\"Picture\"> "
}

function getPElement(data){
    return "<p>" + data +"</p>"
}

function getH2Element(data){
    return "<h2>" + data +"</h2>"
}

function getTime(data){
    return "<span class=\"cd-date\">" + data + "</span>"
}

function getData(){
    data = []
    data[0] = {
        type:1,
        startTime:"12:50"
    }
    data[1] = {
        type:2,
        subType:1,
        startTime:"13:00"
    }
    data[2] = {
        type:2,
        subType:2,
        startTime:"13:10"
    }
    data[3] = {
        type:2,
        subType:3,
        startTime:"13:10"
    }
    data[4] = {
        type:2,
        subType:4,
        startTime:"13:20"
    }
    data[5] = {
        type:2,
        subType:5,
        startTime:"13:30"
    }
    data[6] = {
        type:3,
        subType:1,
        startTime:"13:00"
    }
    data[7] = {
        type:3,
        subType:2,
        startTime:"13:10"
    }
    data[8] = {
        type:3,
        subType:3,
        startTime:"13:10"
    }
    return data;
}