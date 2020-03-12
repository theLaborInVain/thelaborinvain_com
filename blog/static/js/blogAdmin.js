var app = angular.module('TLVBlog', []);

// avoid clashes with jinja2
app.config(['$interpolateProvider', function($interpolateProvider) {
  $interpolateProvider.startSymbol('{a');
  $interpolateProvider.endSymbol('a}');
}]);

// HTML insertion
app.filter('trustedHTML', function($sce) { return $sce.trustAsHtml; } );

app.filter('orderObjectByDate', function(){
 return function(input, attribute) {
    if (!angular.isObject(input)) return input;

    var array = [];
    for(var objectKey in input) {
        array.push(input[objectKey]);
    }

    array.sort(function(a, b) {
        try {
        var dateA = new Date(a[attribute].$date);
        }
        catch(err) {
            dateA = new Date(2020,0,1)
        };

        try {
        var dateB = new Date(b[attribute].$date);
        }
        catch(err) {
            dateB = new Date(2020,0,1)
        };
        return dateA - dateB;
    });

    return array.reverse();
 }
});

// root Controller starts here
app.controller("rootController", function($scope, $http) {

    $scope.scratch = {
        activePanel: null,
    }

    $scope.ui = {
        show_image_asset_creator_modal: false,
        show_posts_asset_creator_modal: false,
        admin_menu_figure_limit: 15,
        admin_menu_post_limit: 15,
        admin_menu_image_limit: 15,
        show_set_new_post_title_from_tag: true,
    }

    $scope.assets = {
        images: null,
        posts: null,
        attachments: null,
        tags: null,
    }

    $scope.new_post = {
        title: null,
        hero_image: null,
        hero_image_preview: undefined,
    }

    $scope.ngOIDListContains = function(oid, list) {
        // looks for an object by oid in a list of JSON-style OIDs
        for (var i = 0; i < list.length; i++) {
            var listObjOID = list[i].$oid;
            if (listObjOID === oid) {
                return i;
            }
        }
        return false;
    };

    $scope.goToURL = function(url) {
        // lets us use ng-click link an anchor tag
        location.replace(url)
    };

    $scope.clickElement = function(elementID) {
        setTimeout(function() {
            document.getElementById(elementID).click()
            $scope.clicked = true;
        }, 0);
    };

    $scope.submitForm = function(form_id) {
	    var form = document.getElementById(form_id);
        form.submit();
    };

	$scope.postForm = function(url) {
		// creates a bogus form; posts it
	    var form = document.createElement("form");
	
    	form.method = "GET";
	    form.action = url;   

	    document.body.appendChild(form);

	    form.submit();
	};


    // sleep time expects milliseconds
    $scope.sleep = function(time) {
        return new Promise((resolve) => setTimeout(resolve, time));
    }


    // helper functions for working with asset lists
    $scope.expandImage = function(image_oid) {
        // retrieves an image object from $scope.assets.images whose OID
        // matches 'image_oid'
//        console.warn('expanding image oid: ' + image_oid);
        for (i = 0; i < $scope.assets.images.length; i++) {
            var imageObject = $scope.assets.images[i];
            if (imageObject._id.$oid === image_oid) {
                return imageObject;
            };
        };
        return {
            error: 'no image with OID: ' + image_oid,
            base_name: '2020-02-26_sanic.webp',
        }
    };

    $scope.flashSavedMessage = function() {
        // fades it in, fades it out
        var element = document.getElementById("savedPopup");
        element.classList.add("visible");
        $scope.sleep(3000).then(() => {
            element.classList.remove("visible");
       });
    };

    $scope.setNewPaintGradient = function(newPaint) {
        for (i = 0; i < newPaint.colors.length; i++) {
            var color = newPaint.colors[i];
            if (i === 0) {
                newPaint.gradient = color;
            } else {
                newPaint.gradient = newPaint.gradient + ', ' + color;
            };
        };
    };

    $scope.createNewTag = function(list) {
        // creates a new tag; pass a list to 'list' to add the new tag to it
        var reqUrl = '/create/tag';
        console.time(reqUrl);
        $http({
            method : "POST",
            url: reqUrl,
            data: {name: $scope.scratch.create_new_tag},
        }).then(function mySuccess(response) {
            console.warn("Tag created!");
            if (list !== undefined) {
                list.push(response.data._id);
                console.warn('added new tag to list:');
                console.warn(list);
            };
            $scope.scratch.create_new_tag = undefined;
            console.timeEnd(reqUrl);
            $scope.loadAssets('tags');
        }, function myError(response) {
            console.error(response.data);
            console.timeEnd(reqUrl);
        });

    };

    $scope.createNewPaint = function(list) {
        console.warn('Creating new paint!');
        console.warn($scope.scratch.newPaint);
        var reqUrl = '/create/paint';
        console.time(reqUrl);
        $http({
            method : "POST",
            url: reqUrl,
            data: $scope.scratch.newPaint,
        }).then(function mySuccess(response) {
            console.warn("Paint created!");
            if (list !== undefined) {
                if (list === null) {list = []};
                list.push(response.data._id);
                console.warn('added new paint to list:');
                console.warn(list);
            };
            $scope.scratch.newPaint = {colors: []};
            console.timeEnd(reqUrl);
            $scope.loadAssets('paints');
        }, function myError(response) {
            console.error(response.data);
            console.timeEnd(reqUrl);
        });

    };

    $scope.createNewPost = function() {
        var reqUrl = "/create/post"
        var postData = $scope.new_post;
        console.warn(postData);

        console.time(reqUrl);
        $http({
            method : "POST",
            url: reqUrl,
            data: postData,
        }).then(function mySuccess(response) {
//            console.warn(response.data);
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


    //
    //  figure management
    //



    $scope.setNewFigure = function() {

        // sets the $scope.new_figure, which is either a blank dict or
        // the object of an existing figure
        function swapOIDs(attr) {
            if ($scope.new_figure[attr] !== undefined) {
                for (i = 0; i < $scope.new_figure[attr].length; i++) {
                    var oidDict = $scope.new_figure[attr][i];
                    if (oidDict !== undefined && typeof oidDict === 'object') {
                        $scope.new_figure[attr].splice(i, 1);
                        $scope.new_figure[attr].splice(i, 0, oidDict.$oid);
                    };
                };
           };
        };

        if ($scope.scratch.editFigure !== undefined) {
            $scope.new_figure = $scope.scratch.editFigure;
            ['concept_art', 'unpainted', 'tags'].forEach(swapOIDs);
        } else {
            $scope.new_figure = {
                name: null,
                publisher: null,
                concept_art: [],
                unpainted: [],
                sculpted_by: undefined,
                longest_dimension: 0,
                tags: [],
            };
        };
        $scope.scratch.editFigure = undefined;
    };


    $scope.toggleFigureTag = function(tag) {
        if ($scope.new_figure.tags === undefined) {
            $scope.new_figure.tags = [];
        };
        var tagIndex = $scope.new_figure.tags.indexOf(tag._id.$oid);
        if (tagIndex === -1) {
            $scope.new_figure.tags.push(tag._id.$oid);
        } else {
            $scope.new_figure.tags.splice(tagIndex, 1);
        };
    };

    $scope.addImageToActiveList = function(image) {
        if ($scope.scratch.activePanel === 'newFigureArtPanel') {
            if ($scope.new_figure.concept_art.indexOf(image._id.$oid) !== -1) {
                console.warn('already added');
            } else {
                $scope.new_figure.concept_art.push(image._id.$oid);
            }
        } else if ($scope.scratch.activePanel === 'newFigureSculpturePanel') {
            if ($scope.new_figure.unpainted.indexOf(image._id.$oid) !== -1) {
                console.warn('already added');
            } else {
                $scope.new_figure.unpainted.push(image._id.$oid);
            }
        } else {
            throw("Active panel '" + $scope.scratch.activePanel + "' does not have an image OID array!")
        };
    };

    $scope.saveFigure = function(operation) {
        var reqUrl = "/" + operation + "/figure"

        if (operation === 'update') {
            reqUrl = reqUrl + '/' + $scope.new_figure._id.$oid
        };

        var postData = $scope.new_figure;
        console.time(reqUrl);
        $http({
            method : "POST",
            url: reqUrl,
            data: postData,
        }).then(function mySuccess(response) {
            $scope.ui.show_figure_edit_modal = undefined;
            $scope.scratch.editFigure = undefined;
            $scope.setNewFigure();
        	$scope.loadAssets('figures');
            console.timeEnd(reqUrl);
        }, function myError(response) {
            console.error(response.data);
            console.timeEnd(reqUrl);
        });
	};


    $scope.init = function() {
        $scope.loadAssets('tags');
        $scope.loadAssets('figures');
        $scope.loadAssets('images');
        $scope.loadAssets('posts');
        $scope.loadAssets('paints');
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
            $scope.flashSavedMessage();
            $scope.loadPost($scope.post._id.$oid);
            console.timeEnd(req_url);
        }, function myError(response) {
            console.error(response.data);
            console.timeEnd(req_url);
        });

    }

    $scope.updateAttachment = function(attachmentObject, data_dict) {
        // POSTs updateDict to the URL for editing posts
        var req_url = "/update/attachment/" + attachmentObject._id.$oid;
        console.time(req_url);
        $http({
            method : "POST",
            url : req_url,
            data: data_dict,
        }).then(function mySuccess(response) {
            console.warn('Attachment update successful!');
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

    $scope.isAttached = function(image_oid) {
        // returns a bool of whether the image is attached
        // if true, the value will be the index of the attachment
        var attached = false;
        for (i = 0; i < $scope.attachments.length; i++) {
            if ($scope.attachments[i].image_id.$oid === image_oid) {
                attached = $scope.attachments[i]._id.$oid;
            };
        };
        return attached
    };

	$scope.tagAttached = function(tag) {
        // checks if a tag is attached to the current post
        if ($scope.post.tags === null) {return false};
        if ($scope.post.tags.length < 1) {return false};
        for (i = 0; i < $scope.post.tags.length; i++) {
            if ($scope.post.tags[i].$oid === tag._id.$oid) {
                return i;
            };
        };
		return false;
	};


    $scope.togglePostAttr = function(attr, object) {
        // if 'attr' is one of the list attributes of $scope.post, this
        // checks $scope.post for the 'attr' attrib; toggles the object into or
        // out of $scope.post[attr]

        console.warn('toggling $scope.post[' + attr + '] attrib: ' + JSON.stringify(object));

        // one, create it if it doesn't exist
        var dict = {}
        if (
            $scope.post[attr] === undefined ||
            $scope.post[attr] === null ||
            $scope.post[attr].length === 0
            )
                {
                    $scope.post[attr] = [];
                    $scope.post[attr].push(object._id);
                    dict[attr] = $scope.post[attr]
                    $scope.updatePost(dict)
                    return true;
                };

        // two, check if object is in $scope.post.attr

        var attached = $scope.ngOIDListContains(object._id.$oid, $scope.post[attr]);

        // three, do the toggle
        if (attached !== false) {
            $scope.post[attr].splice(attached, 1);
        } else {
            $scope.post[attr].push(object._id);
        };

        dict[attr] = $scope.post[attr];
        $scope.updatePost(dict);
		$scope.loadAssets(attr);

    };

    $scope.toggleImage = function(image_oid) {
        if ($scope.edit_post_ui.attachments_toggler === 'hero') {
            $scope.updateHero(image_oid)
        } else if ($scope.edit_post_ui.attachments_toggler === 'attachments') {
            // loop through attachments in scope; create one if there isn't one
            // with this image OID
            var attachment_exists = $scope.isAttached(image_oid);
            if (attachment_exists) {
                var req_url = "/rm/attachments/" + attachment_exists;
                console.time(req_url);
                $http({
                    method : "GET",
                    url : req_url,
                }).then(function mySuccess(response) {
                    $scope.flashSavedMessage();
                    console.timeEnd(req_url);
                    console.warn('Removed attachment!');
                    $scope.loadAttachments();
                }, function myError(response) {
                    console.error(response.data);
                    console.timeEnd(req_url);
                });
            } else {
                var req_url = "/create/attachment";
                console.time(req_url);
                $http({
                    method : "POST",
                    url : req_url,
                    data: {
                        post_id: $scope.post._id.$oid,
                        image_id: image_oid,
                        caption: $scope.post.hero_caption,
                    }
                }).then(function mySuccess(response) {
                    $scope.flashSavedMessage();
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
    
    $scope.loadPost = function(post_oid){

        var req_url = "/get/post/" + post_oid;
        console.time(req_url);
        var loadPostPromise = $http({
            method : "GET",
            url : req_url,
        })

        // set the $scope.post
        loadPostPromise.then(function mySuccess(response) {
            $scope.post = response.data;
            console.timeEnd(req_url);
        }, function myError(response) {
            console.error(response.data);
            console.timeEnd(req_url);
        });

        // set the $scope.figure
        loadPostPromise.then(function mySuccess(response) {
            var fig_url = "/get/figures/" + $scope.post.figure.$oid;
            console.time(fig_url);
            $http({
                method : "GET",
                url : fig_url,
            }).then(function mySuccess(response) {
                $scope.figure = response.data;
                console.timeEnd(fig_url);
            }, function myError(response) {
                console.error(response.data);
                console.timeEnd(fig_url);
            });
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


app.controller("editFigureController", function($scope, $http) {




});
