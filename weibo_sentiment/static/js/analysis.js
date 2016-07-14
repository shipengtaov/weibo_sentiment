$(function(){
	var categories = $('#analysis-categories').val().split(',');
	var sentiment_data = $('#analysis-data').val().split(',');
	var weibo_name = $('#weibo-name').val();
	for(var i=0; i<sentiment_data.length; i++){
		sentiment_data[i] = parseFloat(sentiment_data[i]);
	}
	$('#analysis-result').highcharts({
		chart: {
			type: 'line'
		},
		title: {
			text: weibo_name + ' 的粉丝情绪趋势图',
		},
		xAxis: {
			categories: categories,
			type: 'datetime',
			labels: {
				rotation: -45,
			}
			// tickInterval: 5,
			// max: 5,
		},
		yAxis: {
			title: {
				text: '微博评论的平均情绪值'
			}
		},
		plotOptions: {
			line: {
				dataLabels: {
					enabled: true
				},
				enableMouseTracking: true
			}
		},
		series: [{
			name: '粉丝情绪值',
			data: sentiment_data,
		}
		]
	});
});
