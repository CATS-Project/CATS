<%@page contentType="text/html" pageEncoding="UTF-8" %>
<%@taglib prefix="t" tagdir="/WEB-INF/tags" %>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>


<t:wrapper title="Create corpus">
    <jsp:attribute name="header">
        <script src="<c:url value="/resources/js/angular.min.js"/>"></script>
        <script src="<c:url value="/resources/js/corpus-form.js"/>"></script>
        <script src="<c:url value="/resources/js/draw_map.js"/>"></script>
        
    </jsp:attribute>
    <jsp:body>
        <ul class="collapsible" data-collapsible="accordion">
            <li>
                <div class="collapsible-header ${user.tokenOk ? "" : "active"}"><i class="material-icons">swap_vert</i>Import CSV corpus</div>
                <div class="collapsible-body" style="padding: 1rem;">
                    <div class="row">
                        <div class="col s12">
                            <p>Columns:<br/>Id, Author, Date, Text ,Location, DescriptionAuthor, Name</p>
                            <form action="<c:url value="/corpus/import"/>" enctype="multipart/form-data" method="post">
                                <div class="file-field input-field">
                                    <div class="btn">
                                        <span>File</span>
                                        <input type="file" name="file">
                                    </div>
                                    <div class="file-path-wrapper">
                                        <input class="file-path validate" type="text"/>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="input-field col s12">
                                        <input id="nameC" type="text" class="validate" name="name">
                                        <label for="nameC">New corpus name</label>
                                    </div>
                                </div>
                                <button class="btn waves-effect waves-light" type="submit" name="action">
                                    Submit
                                </button>
                            </form>
                        </div>
                    </div>
                </div>
            </li>
            <c:if test="${user.tokenOk}">
                <li>
                    <div class="collapsible-header active"><i class="material-icons">trending_up</i>Collect tweets</div>
                    <div class="collapsible-body" style="padding: 1rem;"  data-ng-app="corpus-form">
                        <form class="col s12" action="<c:url value="/corpus"/>" method="post" data-submit-Listener>
                            <div class="row">
                                <div class="input-field col s12">
                                    <input id="duration" type="number" class="validate" name="duration">
                                    <label for="duration">Duration (number of days during wich tweets should be collected, exemple
                                        "30")</label>
                                </div>
                            </div>
                            <div class="row">
                                <div class="input-field col s12">
                                    <input id="name" type="text" class="validate" name="name">
                                    <label for="name">New corpus name</label>
                                </div>
                            </div>

                            <c:forEach items="${forms}" var="field">
                                <jsp:include page="${field.value}" />
                            </c:forEach>

                            <button class="btn waves-effect waves-light" type="submit">
                                Collect tweets
                            </button>

                        </form>
                    </div>
                </li>
            </c:if>
        </ul>

        <script src="https://maps.googleapis.com/maps/api/js?key=AIzaSyDg3Kf8HbtHpqVtSoqybLSx_dzFxodJxsM&signed_in=true&libraries=drawing&callback=initMap"
                async defer></script>
    </jsp:body>
</t:wrapper>