package org.unigram.bepj;

public class Pair implements Comparable {
	 private Integer _1;
	 private Integer _2;
	 
	 public Pair(Integer x1, Integer x2) {
		 _1 = x1;
		 _2 = x2;
	 }
	 
	 public int compareTo(Object obj) {
		 Pair that = (Pair) obj;

		 if (this._1 > that._1) {
			 return 1;
		 } else if (this._1 < that._1) {
			 return -1;
		 }
		 
		// if (this._2 > that._2) {
		//	 return 1;
		// } else if (this._2 < that._2) {
		//	 return -1;
		// }	else {
		//	 return 0;
		// }
		return 0;
	}
	 public Integer first() {return _1;}
 
	 public Integer second() {return _2;}
	 
}

