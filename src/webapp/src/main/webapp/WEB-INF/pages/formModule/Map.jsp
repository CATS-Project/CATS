<%@ page contentType="text/html;charset=UTF-8" language="java" %>
<div class="row" data-ng-controller="map">
    <div class="input-field col s12">
        <p>
            <input type="checkbox" id="checkMap" data-ng-model="mapShown"/>
            <label for="checkMap">Use map filter</label>
        </p>
        <div data-ng-show="mapShown">
            <div id="map"></div>
            <input data-ng-if="mapShown" type="hidden" name="location" readonly id="destinationLat"/>
            <input data-ng-if="mapShown" type="hidden" name="location" readonly id="destinationLng"/>
            <input data-ng-if="mapShown" type="hidden" name="location" readonly id="originLat"/>
            <input data-ng-if="mapShown" type="hidden" name="location" readonly id="originLng"/>
        </div>
    </div>
</div>
