var app = angular.module('TLVBlog', []);

// avoid clashes with jinja2
app.config(['$interpolateProvider', function($interpolateProvider) {
  $interpolateProvider.startSymbol('{a');
  $interpolateProvider.endSymbol('a}');
}]);

// HTML insertion
app.filter('trustedHTML', function($sce) { return $sce.trustAsHtml; } );

// root Controller starts here
app.controller("rootController", function($scope, $http) {

    $scope.ui = {
        show_image_asset_creator_modal: false,
        show_posts_asset_creator_modal: false,
    }

    $scope.assets = {
        images: null,
        posts: null,
    }

    $scope.new_post = {
        title: null,
        hero_image: null,
        hero_image_preview: undefined,
    }

    $scope.createNewPost = function() {
        var reqUrl = "/create_post"

        var postData = {
            title: $scope.new_post.title,
            hero_image: $scope.new_post.hero_image,
        }

        console.time(reqUrl);
        $http({
            method : "POST",
            url: reqUrl,
            data: postData,
        }).then(function mySuccess(response) {
            console.warn(response.data);
            $scope.ui.show_posts_asset_creator_modal = undefined;
            $scope.new_post = {
                title: null,
                hero_image: null,
                hero_image_preview: undefined,
            }
            $scope.loadAssets('posts');
            console.timeEnd(reqUrl);
        }, function myError(response) {
            console.error(response.data);
            console.timeEnd(reqUrl);
        });

    }

    $scope.loadAssets = function(asset_type, count) {

        var req_url = "/get/" + asset_type;
        if (count !== undefined) {
            req_url = req_url + '?count=' + count
        }

        console.time(req_url);
        $http({
            method : "GET",
            url : req_url,
        }).then(function mySuccess(response) {
            $scope.assets[asset_type] = response.data;
            console.timeEnd(req_url);
        }, function myError(response) {
            console.error(response.data);
            console.timeEnd(req_url);
        });
    };

    $scope.init = function() {
        $scope.loadAssets('images', 20);
        $scope.loadAssets('posts');
        console.info('rootController initialized!')
    };

    $scope.init();

});
