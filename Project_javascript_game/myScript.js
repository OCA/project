//for restart game
var restart = document.querySelector("#b");

//for grab all the squares
var squares = document.querySelectorAll('td');

///clear all the squares

function clearBoard(){
	for (var i = 0 ; i < squares.length; i++) {
		squares[i].textContent = '';
	}
}

restart.addEventListener('click',clearBoard);

//recomanded method secind first is next method


function changeMarker(){
	if (this.textContent==='') {
		this.textContent = 'X';
	}else if (this.textContent === 'X') {
		this.textContent = 'O';
	}else{
		this.textContent = '';
	}
}

for (var i = 0; i <squares.length; i++) {
	 squares[i].addEventListener('click',changeMarker);
}



/*
//this is a method to make eight cell id and done the progrm a ****method forst
var cellOne = document.querySelector('#one');
 
cellOne.addEventListener('click',function(){
	if (cellOne.textContent === '') {
		cellOne.textContent = 'X';
	}else if (cellOne.textContent === 'X') {
		cellOne.textContent = 'O';
	}else{
		cellOne.textContent = '';
	}
})

*/
/*	var headOne = document.querySelector('#One')
var headTwo = document.querySelector('#Two')
var headThree = document.querySelector('#Three')

headOne.addEventListener('mouseover',function(){
	headOne.textContent = "Mouse Currently Over";
	headOne.style.color = "red";
})

headTwo.addEventListener('click',function(){
	headTwo.textContent = "Clicked On";
	headTwo.style.color = "yellow";
})
headThree.addEventListener('dblclick',function(){
	headThree.textContent = "Double Clicked On";
	headThree.style.color = "green";
})

alert("Welcome to Our Site");
var input = prompt("enter the number or pounds");
alert("your kilogram is "+ input*0.454);
*/

