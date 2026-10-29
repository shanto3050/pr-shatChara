using UnityEditor;
using UnityEngine;

namespace SatChara.Editor
{
    public static partial class VillageBuild
    {
        private static GameObject RoundProp(string name, PrimitiveType type, Vector3 at, Vector3 scale, Material material)
        {
            var ob=GameObject.CreatePrimitive(type); ob.name=name; ob.transform.SetParent(scenery,false);
            ob.transform.position=at; ob.transform.localScale=scale; ob.GetComponent<Renderer>().sharedMaterial=material;
            Object.DestroyImmediate(ob.GetComponent<Collider>());ob.isStatic=true;return ob;
        }
        private static void DecorateCourtyard(GameObject tree)
        {
            var leafMaterial=Surface("Banana Leaf",null,new Color(.17f,.28f,.075f),0,.18f);
            leafMaterial.SetFloat("_Cull",0); EditorUtility.SetDirty(leafMaterial);
            var leaf=BananaLeaf();
            Vector3[] plants={new Vector3(-15,0,20),new Vector3(-16,0,23),new Vector3(20,0,9),new Vector3(21,0,12),new Vector3(-23,0,4),new Vector3(11,0,33)};
            for(int p=0;p<plants.Length;p++)
            {
                float height=2.1f+(p%3)*.28f;
                RoundProp("Banana pseudostem",PrimitiveType.Cylinder,plants[p]+Vector3.up*height*.5f,new Vector3(.26f,height*.5f,.26f),stem);
                for(int i=0;i<8;i++)
                {
                    var ob=new GameObject("Banana leaf",typeof(MeshFilter),typeof(MeshRenderer)); ob.transform.SetParent(scenery,false);
                    ob.transform.position=plants[p]+Vector3.up*height;
                    ob.transform.rotation=Quaternion.Euler((i%3-1)*12,i*137+p*31,0);
                    ob.transform.localScale=Vector3.one*(.8f+(i%3)*.12f);
                    ob.GetComponent<MeshFilter>().sharedMesh=leaf;ob.GetComponent<Renderer>().sharedMaterial=leafMaterial;ob.isStatic=true;
                }
            }
            var distantTree=EnvironmentPrefab("island_tree_01_distant",7);
            // Distant silhouettes break up the bare horizon without entering the court.
            for(int i=0;i<9;i++)
            {
                var ob=(GameObject)PrefabUtility.InstantiatePrefab(distantTree);ob.transform.SetParent(scenery,false);
                ob.transform.position=new Vector3(-48+i*12,0,53+(i%3)*5);
                ob.transform.rotation=Quaternion.Euler(0,i*97,0);ob.transform.localScale=Vector3.one*(1.2f+i%3*.25f);
                foreach(var renderer in ob.GetComponentsInChildren<Renderer>()) renderer.shadowCastingMode=UnityEngine.Rendering.ShadowCastingMode.Off;
            }
            var pump=Surface("Painted Pump",null,new Color(.16f,.3f,.24f),.3f,.22f);
            Vector3 basePoint=new Vector3(14,0,17);
            Block("Tube well concrete apron",basePoint+Vector3.up*.04f,new Vector3(2.5f,.12f,2.2f),plaster,Quaternion.identity);
            RoundProp("Tube well barrel",PrimitiveType.Cylinder,basePoint+Vector3.up*.6f,new Vector3(.17f,.55f,.17f),pump);
            Block("Pump head",basePoint+new Vector3(0,1.18f,0),new Vector3(.25f,.22f,.3f),pump,Quaternion.identity);
            Block("Pump handle",basePoint+new Vector3(0,1.22f,.45f),new Vector3(.065f,.065f,.95f),wood,Quaternion.Euler(-14,0,0));
            Block("Water spout",basePoint+new Vector3(0,.95f,-.24f),new Vector3(.09f,.09f,.45f),pump,Quaternion.identity);
            var clay=Surface("Earthenware",null,new Color(.44f,.23f,.12f),0,.1f);
            for(int i=0;i<3;i++)
            {
                Vector3 pos=basePoint+new Vector3(-.8f-i*.45f,.25f,-.6f+i%2*.4f);
                RoundProp("Clay water vessel",PrimitiveType.Sphere,pos,new Vector3(.42f,.5f,.42f),clay);
                RoundProp("Vessel neck",PrimitiveType.Cylinder,pos+Vector3.up*.24f,new Vector3(.16f,.07f,.16f),clay);
            }
        }
        private static void DecorateHouse(Vector3 center,float width,float depth,Quaternion rotation)
        {
            Vector3 Local(float x,float y,float z)=>center+rotation*new Vector3(x,y,z);
            Block("Raised plinth",Local(0,.09f,0),new Vector3(width+.35f,.18f,depth+.35f),plaster,rotation);
            Block("Doorstep",Local(-width*.23f,.1f,-depth*.5f-.38f),new Vector3(1.45f,.2f,.7f),plaster,rotation);
            Block("Veranda tin awning",Local(0,2.45f,-depth*.5f-.8f),new Vector3(width+.4f,.09f,1.8f),tin,rotation*Quaternion.Euler(-8,0,0));
            for(int side=-1;side<=1;side+=2)
                RoundProp("Veranda timber post",PrimitiveType.Cylinder,Local(side*(width*.5f-.25f),1.15f,-depth*.5f-1.45f),new Vector3(.1f,1.15f,.1f),wood);
            // Close the open triangular ends under the roof with timber boards.
            for(int side=-1;side<=1;side+=2)
                for(int i=0;i<7;i++)
                {
                    float z=(i-3)*depth/7;float rise=.92f*(1-Mathf.Abs(z)/(depth*.5f));
                    if(rise<=0) continue;
                    Block("Gable board",Local(side*(width*.5f+.015f),3+rise*.5f,z),new Vector3(.06f,rise,depth/7+.01f),wood,rotation);
                }
        }
        private static Mesh BananaLeaf()
        {
            string path=Art+"VillageMeshes/BananaLeaf.asset";
            var mesh=AssetDatabase.LoadAssetAtPath<Mesh>(path);if(mesh)return mesh;
            const int segments=10;var vertices=new Vector3[(segments+1)*3];var triangles=new int[segments*12];
            for(int i=0;i<=segments;i++)
            {
                float t=i/(float)segments;float width=Mathf.Sin(t*Mathf.PI)*.38f;
                float y=Mathf.Sin(t*Mathf.PI)*.55f-t*t*.6f;
                vertices[i*3]=new Vector3(-width,y-.08f*width,t*2.5f);
                vertices[i*3+1]=new Vector3(0,y+.035f,t*2.5f);
                vertices[i*3+2]=new Vector3(width,y-.08f*width,t*2.5f);
                if(i==segments)continue;
                for(int half=0;half<2;half++)
                {
                    int at=i*12+half*6,a=i*3+half,b=a+1,c=a+3,d=c+1;
                    triangles[at]=a;triangles[at+1]=c;triangles[at+2]=b;
                    triangles[at+3]=b;triangles[at+4]=c;triangles[at+5]=d;
                }
            }
            mesh=new Mesh{name="Curved banana leaf",vertices=vertices,triangles=triangles};mesh.RecalculateNormals();mesh.RecalculateBounds();
            AssetDatabase.CreateAsset(mesh,path);return mesh;
        }
    }
}
