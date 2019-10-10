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
        attachments: null,
    }

    $scope.new_post = {
        title: null,
        hero_image: null,
        hero_image_preview: undefined,
    }

    $scope.goToURL = function(url) {
        // lets us use ng-click link an anchor tag
        location.replace(url)
    };

    // sleep time expects milliseconds
    $scope.sleep = function(time) {
        return new Promise((resolve) => setTimeout(resolve, time));
    }

    $scope.flashSavedMessage = function() {
        // fades it in, fades it out
        var element = document.getElementById("savedPopup");
        element.classList.add("visible");
        $scope.sleep(3000).then(() => {
            element.classList.remove("visible");
       });
    };

    $scope.createNewPost = function() {
        var reqUrl = "/create/post"

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


    $scope.toggleFullScreenLoading = function() {
        var element = document.getElementById("fullScreenLoading");
        element.classList.toggle("display_none");
    };


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


// root Controller starts here
app.controller("editPostController", function($scope, $http) {

    $scope.edit_post_ui = {
        attachments_toggler: 'hero', 
    };

    $scope.updatePost = function(updateDict) {
        console.warn('Updating post...');
        console.warn(updateDict);
        // POSTs updateDict to the URL for editing posts
        var req_url = "/edit_post/" + $scope.post._id.$oid;
        console.time(req_url);
        $http({
            method : "POST",
            url : req_url,
            data: updateDict
        }).then(function mySuccess(response) {
            console.warn('Update successful!');
            console.warn(response);
            $scope.flashSavedMessage();
            $scope.loadPost($scope.post._id.$oid);
            console.timeEnd(req_url);
        }, function myError(response) {
            console.error(response.data);
            console.timeEnd(req_url);
        });

    }

    $scope.updateHero = function(image_oid) {
        // change the post hero image; reload
        if (image_oid === $scope.post.hero_image._id.$oid) {
            console.warn('This is already the hero image!');
        } else {
            var updateDict = {hero_image: image_oid};
            $scope.updatePost(updateDict);
        };
 
    };

    $scope.toggleImage = function(image_oid) {
        if ($scope.edit_post_ui.attachments_toggler === 'hero') {
            $scope.updateHero(image_oid)
        } else if ($scope.edit_post_ui.attachments_toggler === 'attachments') {
            // loop through attachments in scope; create one if there isn't one
            // with this image OID
            var attachment_exists = false;
            for (i = 0; i < $scope.attachments.length; i++) {
                if ($scope.attachments[i]._id.$oid === image_oid) {
                    attachment_exists = true;
                };
            };
            if (attachment_exists) {
                // pass
            } else {
                var req_url = "/create/attachment";
                console.time(req_url);
                $http({
                    method : "POST",
                    url : req_url,
                    data: {
                        post_id: $scope.post._id.$oid,
                        image_id: image_oid,
                    }
                }).then(function mySuccess(response) {
                    console.timeEnd(req_url);
                    console.warn(response.data);
                    $scope.loadAttachments();
                }, function myError(response) {
                    console.error(response.data);
                    console.timeEnd(req_url);
                });
            };
        };
    };
    
    $scope.getAsset = function(collection, oid){
        // gets an asset; returns a dict
        var req_url = "/get/" + collection + '/' + oid;
        console.time(req_url);
        $http({
            method : "GET",
            url : req_url,
        }).then(function mySuccess(response) {
            console.timeEnd(req_url);
            return response.data;
        }, function myError(response) {
            console.error(response.data);
            console.timeEnd(req_url);
            return null;
        });

    };

    $scope.loadPost = function(post_oid){

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

    $scope.loadAttachments = function() {
//        console.warn('getting attachments: ' + $scope.post._id.$oid)
        var req_url = "/get/attachments/" + $scope.post._id.$oid;
        console.time(req_url);
        $http({
            method : "GET",
            url : req_url,
        }).then(function mySuccess(response) {
            $scope.attachments = response.data;
            console.timeEnd(req_url);
        }, function myError(response) {
            console.error(response.data);
            console.timeEnd(req_url);
        });
    };

    $scope.init = function() {
        console.info('editPostController initialized!')
    };

    $scope.init()
});
