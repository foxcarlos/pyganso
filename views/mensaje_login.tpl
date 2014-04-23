<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="description" content="">
<meta name="viewport" content="width=device-width">
<link rel="stylesheet" href="/static/css/bootstrap.min.css">
<link rel="stylesheet" href="/static/css/style.css">
<link href='http://fonts.googleapis.com/css?family=Cabin+Condensed:400,500,600,700' rel='stylesheet' type='text/css'>
<link href='http://fonts.googleapis.com/css?family=Capriola' rel='stylesheet' type='text/css'>
<title>Mensaje</title>
</head>

<body>
<div class="container">
    <div class="row">
		<div class="col-md-4 col-md-offset-4">
        <img src="/static/img/smssend.png" width="50%" />
    		<div class="panel panel-personal">
			  	<div class="panel-heading">
			    	<h3 class="panel-title">{{cabecera}}<span class="Three-Dee pull-right" >PyLoroWeb</span></h3>
			 	</div>
			  	<div class="panel-body">
			    	
                    <fieldset>
			    	  	<div class="alert alert-warning"><span class="glyphicon glyphicon-asterisk" ></span> {{mensaje}}!</div>
                        
			    		<div class="row boton">
                        
                        <div class="col-xs-12 ">
                         <a href="/" class="align-vertical btn btn-personal">Regresar</a>
                        </div>
                        
                        </div>
			    	</fieldset>
			      	
			    </div>
			</div>
		</div>
	</div>
</div>
</body>
</html>
