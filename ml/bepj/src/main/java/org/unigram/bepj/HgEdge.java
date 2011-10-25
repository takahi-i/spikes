package org.unigram.bepj;

public class HgEdge implements Comparable {
	
	public int[] vertices;
	
	public HgEdge(int[] vertices) {
		super();
		this.vertices = vertices;
	}	

	/**
	public HgEdge(long[] vertices) {
		super();
		this.vertices = new int [3]; // allocate memory!! 		
		this.vertices[0] = (int) vertices[0];
		this.vertices[1] = (int) vertices[1];
		this.vertices[2] = (int) vertices[2];
	}
	*/

	public int compareTo(Object object) {
		 HgEdge a = (HgEdge) object;
		 
		 if (this.vertices[0] < a.vertices[0]) {
			 return 1;
		 } else if (this.vertices[0] > a.vertices[0]) {
			 return -1;
		 }
		 
		 if (this.vertices[1] < a.vertices[1]) {
			 return 1;
		 } else if (this.vertices[1] > a.vertices[1]) {
			 return -1;
		 }
		 
		 if (this.vertices[2] < a.vertices[2]) {
			 return 1;
		 } else if (this.vertices[2] > a.vertices[2]) {
			 return -1;
		 }	else {
			 return 0;
		 }		 
	}

	@Override
	public boolean equals(Object obj) {
		 if ( !(obj instanceof HgEdge) ) return false;
		 HgEdge that = (HgEdge) obj;
	    return
	      (this.vertices[0] == that.vertices[0]) &&
	      (this.vertices[1] == that.vertices[1]) &&
	      (this.vertices[2] == that.vertices[2]);
	}
}
