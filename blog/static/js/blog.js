var app = angular.module('blog', []);

// avoid clashes with jinja2
app.config(['$interpolateProvider', function($interpolateProvider) {
  $interpolateProvider.startSymbol('{a');
  $interpolateProvider.endSymbol('a}');
}]);

// HTML insertion
app.filter('trustedHTML', function($sce) { return $sce.trustAsHtml; } );

// root Controller starts here
app.controller("rootController", function($scope, $http) {

    $scope.scratch = {}
    $scope.ui = {}

    $scope.loadAssets = function(asset_type, count) {

        var reqUrl = "/get/" + asset_type;
        console.time(reqUrl);
        $http({
            method : "GET",
            url : reqUrl,
        }).then(
            function mySuccess(response) {
                $scope[asset_type] = response.data;
                console.timeEnd(reqUrl);
            }, function myError(response) {
                console.error(response.data);
                console.timeEnd(reqUrl);
            }
        );
    };

    $scope.init = function() {
        $scope.loadAssets('tags');
        $scope.loadAssets('posts');
        console.info('rootController initialized!')
    };

    $scope.init();

});
