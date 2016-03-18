<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
<%--
  Created by IntelliJ IDEA.
  User: Nathanael
  Date: 19/10/2015
  Time: 08:24
  To change this template use File | Settings | File Templates.
--%>
<%@ page contentType="text/html;charset=UTF-8" language="java" %>

<html>
<head>
    <title>Welcome !</title>
    <jsp:include page="head.jsp"/>
</head>
<body>
<jsp:include page="../pages/navbar.jsp" />
<div class="container">
    <div class="row">
        <form class="col s12" name='loginForm' action="<c:url value="/j_spring_security_check"></c:url>" method='POST'>
	        <div class="row">
	        	<c:if test="${not empty error}">
					${error}
				</c:if>
				<c:if test="${not empty msg}">
					${msg}
				</c:if>
			</div>
            <div class="row">
                <div class="input-field col s6">
                    <input id="login" name="login" type="text" class="validate" value="">
                    <label for="login">Login</label>
                </div>
                <div class="input-field col s6">
                    <input id="password" name="password" type="password" class="validate" value="">
                    <label for="password">Password</label>
                </div>
            </div>
             <div class="row">
                <div class="col s6">
                    <button class="btn waves-effect waves-light" type="submit">
		                Login
		            </button>
                </div>
                <div class="col s6">
                   <a class=".right-align btn waves-effect waves-light" href="<c:url value="/register"></c:url>">
		                New User ?
		            </a>
                </div>
            </div>
            
            <input type="hidden" name="${_csrf.parameterName}" value="${_csrf.token}" />
        </form>
    </div>
</div>
</body>
</html>
