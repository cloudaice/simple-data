;(function(win, $, undefined){
    $.fn.SVGMap = function(options){
        var defaults = {
            mapName: 'china',
            mapWidth: 500,
            mapHeight: 400,
            stateColorList: ['003399', '0058B0', '0071E1', '1C8DFF', '51A8FF', '82C0FF', 'AAD5FF'],
            stateDataAttr: ['stateInitColor', 'stateHoverColor', 'stateSelectedColor', 'baifenbi'],
            stateDataType: 'json',
            stateSettingsXmlPath: '',
            stateData: {},
            
            strokeWidth: 1,
            strokeColor: 'F9FCFE',

            stateInitColor: 'AAD5FF',
            stateHoverColor: 'feb41c',
            stateSelectedColor: 'E32F02',
            stateDisabledColor: 'eeeeee',

            showTip: true,
            stateTipWidth: 100,
            // stateTipHeight: 50,
            stateTipX: 0,
            stateTipY: -10,
            stateTipHtml: function(stateData, obj){
                return obj.name;
            },

            hoverCallback: function(stateData, obj){},
            clickCallback: function(stateData, obj){},
            external: false
        };
        var opt = $.extend({}, defaults, options), _self = $(this);
        var mapName = opt.mapName,
            mapConfig = eval(mapName + 'MapConfig');

        var stateData = {};

        if(opt.stateDataType == 'xml'){
            var mapSettings = opt.stateSettingsXmlPath;
            $.ajax({
                type: 'GET',
                url: mapSettings,
                async: false,
                dataType: $.browser.msie ? 'text' : 'xml',
                success: function (data) {
                    var xml;
                    if ($.browser.msie) {
                        xml = new ActiveXObject('Microsoft.XMLDOM');
                        xml.async = false;
                        xml.loadXML(data);
                    } else {
                        xml = data;
                    }
                    var $xml = $(xml);
                    $xml.find('stateData').each(function(i) {
                        var $node = $(this),
                            stateName = $node.attr('stateName');

                        stateData[stateName] = {};

                        // var attrs = $node[0].attributes;
                        // alert(attrs);
                        // for(var i in attrs){
                        //     stateData[stateName][attrs[i].name] = attrs[i].value;
                        // }
                        for(var i = 0, len = opt.stateDataAttr.length; i < len; i++){
                            stateData[stateName][opt.stateDataAttr[i]] = $node.attr(opt.stateDataAttr[i]);
                        }
					});

                    // console.log(stateData);

                }
            });
        }else{
            stateData = opt.stateData;
        }

		var ScaleRaphael=function(container,width,height){var wrapper=document.getElementById(container);if(!wrapper.style.position)wrapper.style.position="relative";wrapper.style.width=width+"px";wrapper.style.height=height+"px";wrapper.style.overflow="hidden";var nestedWrapper;if(Raphael.type=="VML"){wrapper.innerHTML="<rvml:group style='position : absolute; width: 1000px; height: 1000px; top: 0px; left: 0px' coordsize='1000,1000' class='rvml' id='vmlgroup_"+container+"'><\/rvml:group>";nestedWrapper=document.getElementById("vmlgroup_"+container);}else{wrapper.innerHTML="<div class='svggroup'><\/div>";nestedWrapper=wrapper.getElementsByClassName("svggroup")[0];}var paper=new Raphael(nestedWrapper,width,height);var vmlDiv;if(Raphael.type=="SVG"){paper.canvas.setAttribute("viewBox","0 0 "+width+" "+height);}else{vmlDiv=wrapper.getElementsByTagName("div")[0];}paper.changeSize=function(w,h,center,clipping){clipping=!clipping;var ratioW=w/width;var ratioH=h/height;var scale=ratioW<ratioH?ratioW:ratioH;var newHeight=parseInt(height*scale);var newWidth=parseInt(width*scale);if(Raphael.type=="VML"){var txt=document.getElementsByTagName("textpath");for(var i in txt){var curr=txt[i];if(curr.style){if(!curr._fontSize){var mod=curr.style.font.split("px");curr._fontSize=parseInt(mod[0]);curr._font=mod[1];}curr.style.font=curr._fontSize*scale+"px"+curr._font;}}var newSize;if(newWidth<newHeight){newSize=newWidth*1000/width;}else{newSize=newHeight*1000/height;}newSize=parseInt(newSize);nestedWrapper.style.width=newSize+"px";nestedWrapper.style.height=newSize+"px";if(clipping){nestedWrapper.style.left=parseInt((w-newWidth)/2)+"px";nestedWrapper.style.top=parseInt((h-newHeight)/2)+"px";}vmlDiv.style.overflow="visible";}if(clipping){newWidth=w;newHeight=h;}wrapper.style.width=newWidth+"px";wrapper.style.height=newHeight+"px";paper.setSize(newWidth,newHeight);if(center){wrapper.style.position="absolute";wrapper.style.left=parseInt((w-newWidth)/2)+"px";wrapper.style.top=parseInt((h-newHeight)/2)+"px";}};paper.scaleAll=function(amount){paper.changeSize(width*amount,height*amount);};paper.changeSize(width,height);paper.w=width;paper.h=height;return paper;}
		
		var offsetXY = function(e){
            var mouseX, 
                mouseY,
                tipWidth = $('.stateTip').outerWidth(),
                tipHeight = $('.stateTip').outerHeight();
            if(e && e.pageX){
                mouseX = e.pageX;
                mouseY = e.pageY;
            }else{
                mouseX = event.clientX + document.body.scrollLeft + document.documentElement.scrollLeft;
                mouseY = event.clientY + document.body.scrollTop + document.documentElement.scrollTop;
            }
            mouseX = mouseX - tipWidth/2 + opt.stateTipX < 0 ? 0 : mouseX - tipWidth/2 + opt.stateTipX;
            mouseY = mouseY - tipHeight + opt.stateTipY < 0 ? mouseY - opt.stateTipY : mouseY - tipHeight + opt.stateTipY;
            return [mouseX, mouseY];
        }

        var current, reTimer;

		var r = new ScaleRaphael($(this).attr('id'), mapConfig.width, mapConfig.height),
            attributes = {
                fill: '#' + opt.stateInitColor,
                cursor: 'pointer',
                stroke: '#' + opt.strokeColor,
                'stroke-width': opt.strokeWidth,
                'stroke-linejoin': 'round'
            };

        
        var stateColor = {};
       
        for (var state in mapConfig.shapes) {
            var thisStateData = stateData[state],
                initColor = '#' + (thisStateData && opt.stateColorList[thisStateData.stateInitColor] || opt.stateInitColor),
                hoverColor = '#' + (thisStateData && thisStateData.stateHoverColor || opt.stateHoverColor),
                selectedColor = '#' + (thisStateData && thisStateData.stateSelectedColor || opt.stateSelectedColor),
                disabledColor = '#' + (thisStateData && thisStateData.stateDisabledColor || opt.stateDisabledColor);
            
            stateColor[state] = {};

            stateColor[state].initColor = initColor;
            stateColor[state].hoverColor = hoverColor;
            stateColor[state].selectedColor = selectedColor;

            var obj = r.path(mapConfig['shapes'][state]);
            obj.id = state;
            obj.name = mapConfig['names'][state];
            obj.attr(attributes);

            if(opt.external){
                opt.external[obj.id] = obj;
            }

            if(stateData[state] && stateData[state].diabled){
            	obj.attr({
            		fill: disabledColor,
            		cursor: 'default'
            	});
            }else{
                obj.attr({
                    fill: initColor
                });
                obj.hover(function(e){
                    if (this != current){
                        this.animate({
                            fill: stateColor[this.id].hoverColor
                        }, 250);
                    }
                    if(opt.showTip){
                        clearTimeout(reTimer);
                        if ($('.stateTip').length == 0) {
                            $(document.body).append('<div class="stateTip"></div');
                        }
                        $('.stateTip').html(opt.stateTipHtml(stateData, this));
                        var _offsetXY = new offsetXY(e);

                        $('.stateTip').css({
                            width: opt.stateTipWidth || 'auto',
                            height: opt.stateTipHeight || 'auto',
                            left: _offsetXY[0],
                            top: _offsetXY[1]
                        }).show();
                    }

                    opt.hoverCallback(stateData, this);
                });

                obj.mouseout(function(){
                    if (this != current) {
                        this.animate({
                            fill: stateColor[this.id].initColor
                        }, 250);
                    }
                    // $('.stateTip').hide();
                    if(opt.showTip){
                        reTimer = setTimeout(function(){
                            $('.stateTip').remove();
                        }, 100);
                    }
                });

                obj.mouseup(function(e) {
                    if(current) {
                        current.animate({
                            fill: stateColor[current.id].initColor
                        }, 250);
                    }

                    this.animate({
                        fill: stateColor[this.id].selectedColor
                    }, 250);

                    current = this;
                    opt.clickCallback(stateData, this);
                });
            }
            r.changeSize(opt.mapWidth, opt.mapHeight, false, false);
        }
        document.body.onmousemove = function(e){
            var _offsetXY = new offsetXY(e);
            $('.stateTip').css({
                left: _offsetXY[0],
                top: _offsetXY[1]
            });
        };
    }
})(this, jQuery);