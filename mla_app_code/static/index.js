	// instantiate NeXt app
	var app = new nx.ui.Application();

	// instantiate Topology class
	var topology = new nx.graphic.Topology({
		// width 100% if true
		'adaptive': false,
		// show icons' nodes, otherwise display dots
		'showIcon': true,
		// special configuration for nodes
		'nodeConfig': {
			'label': 'model.name',
			'iconType': "router",
			'color': '#0how00'
		},
		// special configuration for links
		'linkConfig': {
			'linkType': 'curve'
		},
		// property name to identify unique nodes
		'identityKey': 'name', // helps to link source and target
		// canvas size
		'width': 1000,
		'height': 600,
		// "engine" that process topology prior to rendering
		'dataProcessor': 'force',
		// moves the labels in order to avoid overlay
		'enableSmartLabel': true,
		// smooth scaling. may slow down, if true
		'enableGradualScaling': false,
		// if true, two nodes can have more than one link
		'supportMultipleLink': true,
		// enable scaling
		"scalable": true
	});

topology.on("ready", function(){
  	// load topology data from app/data.js
	topology.data(topologyData);
});


	// bind the topology object to the app
	topology.attach(app);


	//console.log(topology.getNode("Port0"));
	var pathHops = [
		"Port0",
		"Port1",
		"Houston",
		"New Jersey"
	];

	topology.on("topologyGenerated", function() {

		var groupsLayer = topology.getLayer("groups");
		var nodesDict = topology.getLayer("nodes").nodeDictionary();

		var nodes1 = [nodesDict.getItem("Port0"), nodesDict.getItem("Port1"), nodesDict.getItem("Port2")];
		var group1 = groupsLayer.addGroup({
			nodes: nodes1,
			label: 'switch1',
			color: '#f00',
            id: 'group1'
		});

		var nodes2 = [nodesDict.getItem("Port3"), nodesDict.getItem("Port4"),nodesDict.getItem("Port5")];
		var group2 = groupsLayer.addGroup({
			nodes: nodes2,
			label: 'switch2',
			color: '#0f0',
            id: 'group2'
		});


        var nodes3 = [nodesDict.getItem("Port1"),nodesDict.getItem("Port3"),nodesDict.getItem("Port5"),nodesDict.getItem("Port0")];
        var group3 = groupsLayer.addGroup({
            nodes: nodes3,
            label: 'Vlan1',
            color: '#111',
            id: 'group3'
        });  

        var nodes4 = [nodesDict.getItem("Port2"),nodesDict.getItem("Port4")]; //find and replace 
        var group4 = groupsLayer.addGroup({
            nodes: nodes4,
            label: 'Vlan2',
            color: '#eee',
            id: 'group4'
        });   
    // groupsLayer.removeGroup("group1");
    
	});


var topologyData = {
	// define 3 nodess
	"nodes": [
		{
			"id": 0,
			"name": "Port0",
			"x": 10,
			"y": 10

		},
		{
			"id": 1,
			"name": "Port1",
			"x": 10,
			"y": 20
		},
		{
			"id": 2,
			"name": "Port2",
			"x": 20,
			"y": 10
		},
		{
			"id": 3,
			"name": "Port3",
			"x": 20,
			"y": 20
		},
		{
			"id": 4,
			"name": "Port4",
			"x": 30,
			"y": 10
		},
		{
			"id": 5,
			"name": "Port5",
			"x": 10,
			"y": 30
		}
	]
};