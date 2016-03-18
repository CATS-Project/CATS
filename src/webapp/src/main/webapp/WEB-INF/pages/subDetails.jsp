<%@ taglib prefix="t" tagdir="/WEB-INF/tags" %>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
<%@ page contentType="text/html;charset=UTF-8" language="java" %>
<t:wrapper title="Sub-Corpus Details">
	<jsp:attribute name="header">
       
    </jsp:attribute>
    <jsp:body>
        <div class="row" style="padding-top: 1rem;">
            <div class="col s12">
                <a  href="<c:url value="/sub/${sub.id}/sub.csv"/>" download class="waves-effect waves-light btn">
                    <i class="material-icons right">import_export</i>Dowload my sub corpus in CSV</a>
            </div>
        </div>

        <div class="row" style="padding-top: 1rem;">
        	<div class="input-field col s6">
                <label>Sub corpus Name : ${sub.name}</label>
            </div>
            <div class="input-field col s6">
                <label>Regular Expression : ${sub.regex}</label>
            </div>
        </div>
        
        <div class="row" style="padding-top: 1rem;">
        	<div class="input-field col s6">
                <label>Hashtags : 
               		<c:forEach var="entry" items="${sub.hashtags}" >
                        ${entry}, 
                    </c:forEach>
                 </label>
            </div>
            <div class="input-field col s6">
                <label>Mentions : 
                	<c:forEach var="entry" items="${sub.mentions}" >
                        ${entry}, 
                    </c:forEach>
                </label>
            </div>
        </div>
        <div class="row" style="padding-top: 1rem;">
        	<div class="input-field col s6">
                <label>Date de création : ${sub.creationDate}
                 </label>
            </div>
        </div>
    </jsp:body>
</t:wrapper>
