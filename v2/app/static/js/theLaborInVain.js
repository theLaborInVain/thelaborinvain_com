"use strict";

var app = angular.module('theLaborInVain', ['ngAnimate']);

// avoid clashes with jinja2
app.config(['$interpolateProvider', function($interpolateProvider) {
    $interpolateProvider.startSymbol('{a');
    $interpolateProvider.endSymbol('a}');
}]);

app.controller('rootScopeController', function($scope, $rootScope, $http) {

    $rootScope.init = function() {
        $rootScope.curDate = new Date();
        console.info('Initialized in $rootScope!');
    };
    $rootScope.init();

    $rootScope.loadUrl = function(destination) {
       // allows us to use ng-click to re-direct to URLs
        window.location = destination;
    };

});
