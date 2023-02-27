	$('#next_page').click(function(){
		if ($(".quiz_section")[quiz_page + 1]){
			if ($(".quiz_section")[quiz_page])	$($(".quiz_section")[quiz_page]).css("display","none");
			quiz_page += 1;
			$($(".quiz_section")[quiz_page]).css("display","inline-block");
		}
		calculate_percentage();
	});

	$('#pervious_page').click(function(){
		if ($(".quiz_section")[quiz_page - 1]){
			if ($(".quiz_section")[quiz_page])	$($(".quiz_section")[quiz_page]).css("display","none");
			quiz_page -= 1;
			$($(".quiz_section")[quiz_page]).css("display","inline-block");
		}
		calculate_percentage()
	});

	var options = {
	  valueNames: [ 'value' ]
	};

	$('.quiz_section').each(function(e,i){
		if (i.id){
			var userList = new List(i.id, options);
        }
	});

	window.onkeydown = function(key){
		if ($('*:focus')[0] && $('*:focus')[0].tagName == 'TEXTAREA') return true;
		if (key.code == "Enter"){ $("#next_page").click(); return false;};
		if ($('*:focus')[0] && $('*:focus')[0].type && $('*:focus')[0].type == 'text') return true;
		if (key.code == "ArrowLeft"){ $("#pervious_page").click(); return false;};
		if (key.code == "ArrowRight"){ $("#next_page").click(); return false;};
	}

	function calculate_percentage()
	{
		tmp = (quiz_page + 1) / $('.quiz_section').length;
		$("#progress_bar").css('width', 'calc(' + tmp + ' * 90vw)');
	}

	quiz_page = -1;
	$('#next_page').click();
	calculate_percentage()

	$('.helper').each(function(e,i){
		$(i).click(function(){$(this).css('visibility','hidden')});
	})

	$(function () {
  		$('[data-toggle="tooltip"]').tooltip()
	})

	var qz_f_s = 20;

	function qz_plus(){
		qz_f_s += 2;
		$('.content').css('font-size', qz_f_s + 'px');
	}

	function qz_minus(){
		qz_f_s -= 2;
		$('.content').css('font-size', qz_f_s + 'px');
	}

	function qz_all(){
		$('.quiz_section').css('display', 'inline-block');
		$('.quiz_section').css('height', 'inherit');
		$('.quiz_section').css('overflow', 'inherit');
		$('.quiz_section').css('border', 'inherit');
		$('.quiz_section').css('border-top', '1px black dotted');
		$('.quiz_section').css('padding', '0.2em');
		$('#bot_nav').css('display', 'none');
		$('#progress_bar').css('display', 'none');
		qz_f_s += 0;
		qz_f_s = 20;
		$('.content').css('font-size', qz_f_s + 'px');
	}

	function qz_all_no(){
		$('.quiz_section').css('display', 'none');
		$($('.quiz_section')[0]).css('display', 'inline-block');
		$('.quiz_section').css('height', '');
		$('.quiz_section').css('overflow', '');
		$('.quiz_section').css('border', '');
		$('.quiz_section').css('border-top', '');
		$('.quiz_section').css('padding', '');
		$('#bot_nav').css('display', 'block');
		$('#progress_bar').css('display', 'block');
		qz_f_s += 0;
		qz_f_s = 20;
		$('.content').css('font-size', qz_f_s + 'px');
	}

	function showmodal(e)
	{
		$.get(e.href + '?get___txt=1', function(res){
			res = res.replace(/([^\\])',([^'])/g,"$1',\n$2");
			res = res.replace(/"/g, '\\"');
			res = res.replace(/\\x/g, '\\u00');
			res = res.replace(/'/g, '"');
			
			data = JSON.parse(res);
			ht = "";
			for (el in data){
				ht += '<span style="display:inline-block;width:300px;">' + el + "</span>: " + data[el] + '<hr/>';
			}
			$('.helper').html(ht);
			$('.helper').css('visibility','visible');
		});
		event.preventDefault();
	}

	$('.slider').slider({
    	tooltip_position:'bottom',
	});