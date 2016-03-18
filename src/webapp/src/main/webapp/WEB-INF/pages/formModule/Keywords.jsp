<%@ page contentType="text/html;charset=UTF-8" language="java" %>
<div class="row" data-ng-controller="KeyWordsController">
    <div class="input-field col s12">
        <h5>Keywords filter</h5>

        <!--<div class="chip" data-ng-repeat="n in keywords track by $index">
            {{n}}
            <i class="material-icons" data-ng-click="remove($index)">close</i>
        </div>-->

        <ul class="add-list">
            <li data-ng-repeat="n in keywords track by $index">
                <div class="row">
                    <div class="input-field col s9">
                        <input type="text" class="validate no-margin" title="keyword" data-ng-model="keywords[$index]" data-ng-focus="focus($index)" name="keyword"/>
                    </div>
                    <div class="input-field col s3" data-ng-click="remove($index)" style="cursor: pointer;">
                        <i class="material-icons" data-ng-show="$index!=0">close</i>
                    </div>
                </div>
            </li>
        </ul>
    </div>
</div>
