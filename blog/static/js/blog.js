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

    $scope.metaTags = 'painted miniatures, painted'

    $scope.ui = {curDate: new Date()};
    $scope.gallery = {};

    $scope.goToURL = function(url) {
    // lets us use ng-click link an anchor tag
        location.replace(url)
    };

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

    $scope.loadAttachments = function(post, initializeGallery) {
		// gets attachments for 'post'; adds them to the post obj
        // initialize the gallery on the way out
        var req_url = "/get/attachments/" + post._id.$oid;
        console.time(req_url);
        $http({
            method : "GET",
            url : req_url,
        }).then(function mySuccess(response) {
            post.attachments = response.data;
            if (initializeGallery) {
                console.info('Initializing gallery...');
                $scope.initializeGallery();
            }
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

    $scope.extendMetaTags = function(tag_name) {
        $scope.metaTags = $scope.metaTags + ', ' + tag_name
        console.warn($scope.metaTags);
    };

    // tag search

    $scope.showTagSearchResults = function(tagName) {

        $scope.tagSearch = {
            tagName: tagName,
        };
        $scope.tagSearch.results = undefined;

        // get the results
        var req_url = "/search/posts?tag=" + tagName;
        console.time(req_url);
        $http({
            method : "GET",
            url : req_url,
        }).then(function mySuccess(response) {
            $scope.tagSearch.results = response.data;
            console.timeEnd(req_url);
        }, function myError(response) {
            console.error(response.data);
            console.timeEnd(req_url);
        });

        $scope.ui.show_tag_search = true
    }

    // photo gallery stuff below!

    $scope.showPhotoGallery = function(startImage) {
        // unhides the photogallery; uses 'startImage' to determine which image
        // the user starts on
        $scope.ui.show_photo_gallery = true;
        $scope.gallery.current_image = startImage;
    };

    $scope.navigateGallery = function(operation) {
        var current_index = $scope.gallery.imageBaseNames.indexOf($scope.gallery.current_image);

        if (operation === 'next') {
            current_index++ 
        } else (
            current_index-- 
        )

        // handle wrap-arounds
        if (current_index == $scope.gallery.imageBaseNames.length) {
            current_index = 0;
        } else if (current_index == -1) {
            current_index = $scope.gallery.imageBaseNames.length - 1;
        };

        // set it and return
        $scope.gallery.current_image = $scope.gallery.imageBaseNames[current_index];
    }

    $scope.initializeGallery = function() {
        $scope.gallery.imageBaseNames = [$scope.post.hero_image.base_name];
        $scope.gallery.captions = {};
        $scope.gallery.captions[$scope.post.hero_image.base_name] = $scope.post.hero_caption;
   
        for (i = 0; i < $scope.post.attachments.length; i++) {
            $scope.gallery.imageBaseNames.push($scope.post.attachments[i].image.base_name);
            $scope.gallery.captions[$scope.post.attachments[i].image.base_name] = $scope.post.attachments[i].caption;
        };
        $scope.gallery.current_image = $scope.gallery.imageBaseNames[0];
        console.warn('Initialized gallery!');
    };



    $scope.init = function() {
        $scope.loadAssets('tags');
        $scope.loadAssets('posts');
        console.info('rootController initialized!')
    };

    $scope.init();


});
