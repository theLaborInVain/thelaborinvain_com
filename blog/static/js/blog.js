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

    $scope.scratch = {};

    $scope.ui = {curDate: new Date()};

    $scope.loadAssets = function(asset_type, count) {

        var reqUrl = "/get/" + asset_type;
        if (count !== undefined) {
          req_url = reqUrl + '?count=' + count
        }

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

    $scope.loadAttachments = function(post) {
		// gets attachments for 'post'; adds them to the post obj
        var req_url = "/get/attachments/" + post._id.$oid;
        console.time(req_url);
        $http({
            method : "GET",
            url : req_url,
        }).then(function mySuccess(response) {
            post.attachments = response.data;
            console.timeEnd(req_url);
        }, function myError(response) {
            console.error(response.data);
            console.timeEnd(req_url);
        });
    };

    $scope.setPost = function(post_oid) {
		// gets attachments for 'post'; adds them to the post obj
        var req_url = "/get/post/" + post_oid;
        console.time(req_url);
        $http({
            method : "GET",
            url : req_url,
        }).then(function mySuccess(response) {
            $scope.post = response.data;
            console.timeEnd(req_url);
        }, function myError(response) {
            console.error(response.data);
            console.timeEnd(req_url);
        });
    };

    $scope.getTag = function(oid) {
        // returns a tag object; consoles an error if it can't
        for (i = 0; i < $scope.tags.length; i++) {
            if ($scope.tags[i]._id.$oid === oid.$oid) {
                return $scope.tags[i]
            };
       };
       console.error('Could not find tag with OID ' + oid);
    };

    $scope.init = function() {
        $scope.loadAssets('tags');
        $scope.loadAssets('posts');
        console.info('rootController initialized!')
    };

    $scope.init();

});
