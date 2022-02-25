"use strict";

var app = angular.module('theLaborInVain', ['ngAnimate']);

app.controller('rootScopeController', function($scope, $rootScope, $http) {

    $rootScope.init = function() {
        console.info('Initialized in $rootScope!');
    };
    $rootScope.init();
});
