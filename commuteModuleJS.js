var home = "38.975989,-77.363236";
var work = "38.893514,-77.047873";

function displayHome(){
	return document.write(home);
}function displayWork(){
	return document.write(work);
}
function getCommute(){
	var Httpreq = new XMLHttpRequest();
	var theURL = "http://www.mapquestapi.com/directions/v2/route?key=Fmjtd%7Cluur2h02nh%2C7l%3Do5-9wb2gz&from="+home+"&to="+work;
	Httpreq.open("GET",theURL,false);
	Httpreq.send(null);
	var array = Httpreq.responseText;
	processCommute(array);
	return 0;
}
function processCommute(response){
	var json = JSON.parse(response);
	document.write(Math.round((json.route.realTime)/60));
	return 0;
}