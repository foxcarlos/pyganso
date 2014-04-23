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
<script src="//code.jquery.com/jquery-1.10.2.min.js"></script>
<script type="text/javascript" src="/static/js/contador.js" ></script>
<title>PyLoro SMS</title>
</head>

<body>
<div class="container">
    <div class="row">
		<div class="col-md-4 col-md-offset-4">
        <div class="row">
        <div class="col-xs-6"><img src="/static/img/smssend.png" width="100%" /></div>
        <div class="col-xs-6" ></div>
        </div>
    		<div class="panel panel-personal">
			  	<div class="panel-heading">
			    	<h3 class="panel-title">Envio de SMS  <span class="Three-Dee pull-right" >PyLoroWeb</span></h3>
			 	</div>
			  	<div class="panel-body">
			    	<form accept-charset="UTF-8"  role="form" action="/smsenviar" method="post">
                    <fieldset>
			    	  	<div class="input-group form-group">
                        <span class="input-group-addon"><i class="glyphicon glyphicon-phone"></i></span>
			    		    <input class="form-control" placeholder="Celular" name="numero" maxlength="16" type="text">
			    		</div>
                        
			    		<div class="form-group">
                        <textarea class="form-control counted" name="comentarios" placeholder="Mensaje a Enviar" rows="5" maxlength="140" ></textarea>
                        <h5 class="pull-right" id="counter">140 caracteres restantes</h5>
			    		</div>
                        
			    		<div class="row boton">
                        
                        <div class="col-xs-12 ">
                        <input class="btn btn-personal" type="submit" value="Enviar"> 
                        </div>
                        
                        </div>
			    	</fieldset>
			      	</form>
			    </div>
			</div>
		</div>
	</div>
</div>

</body>
</html>
