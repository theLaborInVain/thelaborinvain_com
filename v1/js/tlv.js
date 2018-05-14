var app = angular.module('tlvApp', []);

app.filter('trustedHTML',
   function($sce) {
      return $sce.trustAsHtml;
   }
);

app.controller('bodyController', function($scope, $http) {

})
