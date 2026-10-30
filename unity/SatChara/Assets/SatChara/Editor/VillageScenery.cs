using UnityEditor;
using UnityEngine;

namespace SatChara.Editor
{
    public static partial class VillageBuild
    {
        private static Transform scenery;
        private static GameObject Block(string name, Vector3 position, Vector3 size, Material material, Quaternion rotation)
        {
            var ob = GameObject.CreatePrimitive(PrimitiveType.Cube);
            ob.name = name; ob.transform.SetParent(scenery, false);
            ob.transform.position = position; ob.transform.localScale = size; ob.transform.rotation = rotation;
            ob.GetComponent<Renderer>().sharedMaterial = material;
            Object.DestroyImmediate(ob.GetComponent<Collider>());
            ob.isStatic = true; return ob;
        }
        private static void BuildCourtyard()
        {
            ImportedCourtyard();
        }

        private static void House(Vector3 center,float width,float depth,float yaw)
        {
            Quaternion rotation=Quaternion.Euler(0,yaw,0);
            DecorateHouse(center,width,depth,rotation);
            Block("Plastered house",center+Vector3.up*1.5f,new Vector3(width,3,depth),plaster,rotation);
            for(int side=-1;side<=1;side+=2)
            {
                Vector3 offset=rotation*new Vector3(0,3.35f,side*(depth*.25f));
                Block("Weathered pitched tin roof",center+offset,new Vector3(width+1,.1f,depth*.56f+ .6f),tin,rotation*Quaternion.Euler(side*20,0,0));
            }
            Block("Wooden door",center+rotation*new Vector3(-width*.23f,1.05f,-depth*.5f-.025f),new Vector3(1.1f,2.1f,.08f),wood,rotation);
            for(int i=0;i<2;i++)
                Block("Window shutters",center+rotation*new Vector3(width*(.05f+i*.23f),1.7f,-depth*.5f-.04f),new Vector3(1,.95f,.09f),wood,rotation);
        }
        private static Mesh StoneMesh()
        {
            const string path=Art+"VillageMeshes/RiverStone.asset";
            var mesh=AssetDatabase.LoadAssetAtPath<Mesh>(path); if(mesh) return mesh;
            const int sides=12;
            var vertices=new Vector3[sides*2+2];var indices=new int[sides*12];
            for(int ring=0;ring<2;ring++) for(int i=0;i<sides;i++)
            {
                float angle=i*Mathf.PI*2/sides;float radius=1+Mathf.Sin(i*2.7f)*.07f;
                vertices[ring*sides+i]=new Vector3(Mathf.Cos(angle)*radius,ring==0?-.5f:.5f,Mathf.Sin(angle)*radius);
            }
            vertices[sides*2]=Vector3.down*.5f;vertices[sides*2+1]=Vector3.up*.5f;
            int at=0;
            for(int i=0;i<sides;i++)
            {
                int n=(i+1)%sides;
                int[] face={i,i+sides,n+sides,i,n+sides,n,sides*2,n,i,sides*2+1,i+sides,n+sides};
                foreach(int index in face) indices[at++]=index;
            }
            mesh=new Mesh{name="Flattened river stone",vertices=vertices,triangles=indices};mesh.RecalculateNormals();mesh.RecalculateBounds();
            AssetDatabase.CreateAsset(mesh,path);return mesh;
        }
    }
}
