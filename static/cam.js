setInterval(function(){
	$("#cam_image").attr("src", "output.jpg?time="+new Date().getTime());
},250);
