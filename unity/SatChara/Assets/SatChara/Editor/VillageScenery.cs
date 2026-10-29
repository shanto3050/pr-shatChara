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
        private static void BuildCourtyard(GameObject tree, GameObject barrel)
        {
            scenery = new GameObject("Village surroundings").transform;
            Block("Packed earth", new Vector3(0,-.12f,0), new Vector3(180,.2f,200), earth, Quaternion.identity);
            House(new Vector3(-20,0,13), 10, 7, 12);
            House(new Vector3(17,0,20), 11, 6, -12);
            House(new Vector3(2,0,29), 9, 6, 3);
            DecorateCourtyard(tree);
            // Decoration stays outside the playable bounds (x +/- 11, z +/- 14).
            for(int side=-1;side<=1;side+=2)
                for(int i=0;i<15;i++)
                {
                    float z=-21+i*3.2f;
                    Block("Bamboo fence post",new Vector3(side*17, .8f,z),new Vector3(.09f,1.6f,.09f),wood,Quaternion.Euler(0,0,(i%3-1)*3));
                    if(i<14) for(int rail=0;rail<2;rail++)
                        Block("Bamboo rail",new Vector3(side*17,.6f+rail*.6f,z+1.6f),new Vector3(.07f,.07f,3.3f),wood,Quaternion.identity);
                }
            Vector3[] trees={new Vector3(-26,0,-8),new Vector3(25,0,-4),new Vector3(-29,0,22),new Vector3(27,0,29),new Vector3(-10,0,37),new Vector3(11,0,39)};
            for(int i=0;i<trees.Length;i++)
            {
                var ob=(GameObject)PrefabUtility.InstantiatePrefab(tree); ob.transform.SetParent(scenery,false);
                ob.transform.position=trees[i]; ob.transform.rotation=Quaternion.Euler(0,i*73,0); ob.transform.localScale=Vector3.one*(1+i%3*.22f);
            }
            for(int i=0;i<3;i++)
            {
                var ob=(GameObject)PrefabUtility.InstantiatePrefab(barrel);ob.transform.SetParent(scenery,false);
                ob.transform.position=new Vector3(12+i*.9f,0,23+i%2);ob.transform.rotation=Quaternion.Euler(0,i*43,0);
            }
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
