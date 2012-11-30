function myXMLHttpRequest ()
{
	var xmlhttplocal;
	try {
		xmlhttplocal = new ActiveXObject ("Msxml2.XMLHTTP")}
	catch (e) {
		try {
			xmlhttplocal = new ActiveXObject ("Microsoft.XMLHTTP")
		}
		catch (E) {
			xmlhttplocal = false;
		}
	}
	if (!xmlhttplocal && typeof XMLHttpRequest != 'undefined') {
		try {
			var xmlhttplocal = new XMLHttpRequest ();
		}
		catch (e) {
	  		var xmlhttplocal = false;
			alert ('couldn\'t create xmlhttp object');
		}
	}
	return (xmlhttplocal);
}

var testxmlhttp = Array ();
var testString = Array ();
var xmlhttp = new myXMLHttpRequest ();

function pilla (id)
{
	if (xmlhttp) {
		url = "test.html";
		testxmlhttp = new myXMLHttpRequest ();
		if (testxmlhttp) {
			testxmlhttp.open ("GET", url, true);
			testxmlhttp.send (null);

			warnmatch = new RegExp ("^WARN:");
			errormatch = new RegExp ("^ERROR:");
			target = document.getElementById (id);
			target.style.backgroundColor = '#FF9400';
			testxmlhttp.onreadystatechange = function () {
				if (testxmlhttp.readyState == 4) {
					testString = testxmlhttp.responseText;
					if (testString.match (errormatch)) {
						testString = testString.substring (6, testString[0].length);
						alert (testString);
					} else {
						// Just a warning, do nothing
						if (testString.match (warnmatch)) {
							alert(testString);
						} else {
							eval(testString);
							target.innerHTML = '<p>' + foo + ':' + bar + '</p>';
						}
					}
				}
			}
		} else {
			alert('No se pudo crear el objeto XmlHttpRequest');
		}
	}
}
